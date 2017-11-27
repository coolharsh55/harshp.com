import arrow
import asyncio
import concurrent
import json
import redis
from django.utils import timezone
from apps.models.gnib import GNIBAppointment, VisaAppointment
from scripts.gnib_appointments_async import get_gnib_appointments
from scripts.gnib_appointments_async import get_visa_appointments
from django_cron import CronJobBase, Schedule


kvstore = redis.StrictRedis(
    host='localhost', port=6379, db=0, decode_responses=True)


def add_gnib_appointment_to_database(category, category_type, timestamp):
    appointment = GNIBAppointment()
    if category == 'Study':
        appointment.category = GNIBAppointment.CATEGORY_STUDY
    elif category == 'Work':
        appointment.category = GNIBAppointment.CATEGORY_WORK
    elif category == 'Other':
        appointment.category = GNIBAppointment.CATEGORY_OTHER
    if category_type == 'New':
        appointment.category_type = GNIBAppointment.CATEGORY_TYPE_NEW
    elif category_type == 'Renewal':
        appointment.category_type = \
            GNIBAppointment.CATEGORY_TYPE_RENEWAL
    # convert string to datetime using arrow
    appointment.timestamp = arrow.get(
        timestamp, 'DD MMMM YYYY - HH:mm').datetime
    # check if appointment exists
    try:
        existing_appointment = GNIBAppointment.objects.get(
            category=appointment.category,
            category_type=appointment.category_type,
            timestamp=appointment.timestamp)
        if existing_appointment.booked:
            existing_appointment.booked = None
            existing_appointment.save()
    except GNIBAppointment.DoesNotExist:
        appointment.save()


def add_visa_appointment_to_database(category, timestamp):
    appointment = VisaAppointment()
    if category == 'I':
        appointment.category = VisaAppointment.CATEGORY_INDIVIDUAL
    elif category == 'F':
        appointment.category = VisaAppointment.CATEGORY_FAMILY
    # convert string to datetime using arrow
    # FIXME: the date format used by visa appointments is different
    appointment.timestamp = arrow.get(
        timestamp, 'DD/MM/YYYY - HH:mm').datetime
    # check if appointment exists
    try:
        existing_appointment = VisaAppointment.objects.get(
            category=appointment.category,
            category_type=appointment.category_type,
            timestamp=appointment.timestamp)
        if existing_appointment.booked:
            existing_appointment.booked = None
            existing_appointment.save()
    except VisaAppointment.DoesNotExist:
        appointment.save()


def gnib_mark_booked_appointments(booked, category, category_type):
    for appointment in booked:
        if category == 'Study':
            category = GNIBAppointment.CATEGORY_STUDY
        elif category == 'Work':
            category = GNIBAppointment.CATEGORY_WORK
        elif category == 'Other':
            category = GNIBAppointment.CATEGORY_OTHER
        if category_type == 'New':
            category_type = GNIBAppointment.CATEGORY_TYPE_NEW
        elif category_type == 'Renewal':
            category_type = \
                GNIBAppointment.CATEGORY_TYPE_RENEWAL
        # convert string to datetime using arrow
        appointment = arrow.get(
            appointment, 'DD MMMM YYYY - HH:mm').datetime
        # check if appointment exists
        try:
            existing_appointment = GNIBAppointment.objects.get(
                category=category,
                category_type=category_type,
                timestamp=appointment)
            existing_appointment.booked = timezone.now()
            existing_appointment.save()
        except GNIBAppointment.DoesNotExist:
            pass


def visa_mark_booked_appointments(booked, category):
    for appointment in booked:
        if category == 'I':
            category = VisaAppointment.CATEGORY_INDIVIDUAL
        elif category == 'F':
            category = VisaAppointment.CATEGORY_FAMILY
        # convert string to datetime using arrow
        appointment = arrow.get(
            appointment, 'DD/MM/YYYY - HH:mm').datetime
        # check if appointment exists
        try:
            existing_appointment = VisaAppointment.objects.get(
                category=category,
                timestamp=appointment)
            existing_appointment.booked = timezone.now()
            existing_appointment.save()
        except VisaAppointment.DoesNotExist:
            pass


def set_appointments_in_redis(key, appointments):
    booked = []
    added = []
    others = []

    previous = kvstore.get(key)
    if previous is None:
        kvstore.set(key, json.dumps(appointments))
        return
    # at this point, we have previous values
    # and we compare, if any of the appointments are new or missing
    previous = json.loads(previous)

    for item in appointments:
        if item in previous:
            others.append(item)
        else:
            added.append(item)
    for item in previous:
        if item not in others:
            booked.append(item)

    kvstore.set(key, json.dumps(appointments))
    return added, booked


def get_tasks():
    '''create tasks for asyncio'''
    async def gnib_task(category, category_type):
        results = get_gnib_appointments(category, category_type)['data']
        for result in results:
            add_gnib_appointment_to_database(category, category_type, result)
        added, booked = set_appointments_in_redis(
            'gnib_' + category + '_' + category_type, results)
        gnib_mark_booked_appointments(booked, category, category_type)

    async def visa_task(category):
        results = get_visa_appointments(category)['data']
        for result in results:
            add_visa_appointment_to_database(category, result)
        added, booked = set_appointments_in_redis('visa_' + category, results)
        visa_mark_booked_appointments(booked, category)

    return [
        gnib_task('Study', 'New'),
        gnib_task('Study', 'Renewal'),
        gnib_task('Work', 'New'),
        gnib_task('Work', 'Renewal'),
        gnib_task('Other', 'New'),
        gnib_task('Other', 'Renewal'),
        visa_task('I'),
        visa_task('F'),
    ]


async def run_job():
    phases = get_tasks()
    completed, pending = await asyncio.wait(phases, timeout=2)
    kvstore.set('gnib_last_run', timezone.now().strftime('%H:%M'))
    return


def check_gnib_appointments():
    '''retrieve gnib appointments and store them
    Stores GNIB appointments, Visa appointments, and the raw JSON response
    Stores the current appointments in Redis under gnib_appointments_current'''
    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(run_job())
        executor = concurrent.futures.ThreadPoolExecutor(5)
        event_loop.set_default_executor(executor)
    finally:
        # event_loop.close()
        pass


class GnibAppointmentJob(CronJobBase):
    '''gnib appointment check'''
    TICK = 1  # run every X mins
    schedule = Schedule(run_every_mins=TICK)
    code = 'apps.gnib.check_gnib_appointments'

    def do(self):
        check_gnib_appointments()


if __name__ == '__main__':
    pass
