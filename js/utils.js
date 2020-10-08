// converts ISO timestamps to simpler ones
document.addEventListener('DOMContentLoaded', function () {
    let items = document.getElementsByClassName('timestamp');
    for(let item of items) {
        item.innerHTML = dayjs(item.innerHTML).format("D MMM YY");
    }
}, false);

// provides sorting options for lists of elements
document.addEventListener('DOMContentLoaded', function() {
    let lists = document.getElementsByClassName('list-sort');
    for(let list of lists) {
        // list attributes are explicitly declared in the list parent node
        // using the property data-attributes
        // for each <li> in the list the attribute should be defined
        // e.g. <ol data-attributes="x,y">
        // e.g. <li data-x="1" data-y="2">
        let attributes = list.getAttribute('data-attributes');
        if (attributes == null || attributes == "") continue;

        attributes = attributes.split(',')
        let parent = list.parentNode ;
        let list_filter = document.createElement("span");
        list_filter.classList.add('list-filter');
        for (let attribute of attributes) {
            let attribute_span = document.createElement("button");
            attribute_span.innerHTML = attribute;
            attribute_span.classList.add('list-sort-attribute');
            attribute_span.setAttribute('data-for', 'data-'+attribute);
            attribute_span.setAttribute('data-sort-direction', 'asc');
            attribute_span.onclick = list_filter_sort_click_handler;
            list_filter.appendChild(attribute_span);
        }
        parent.insertBefore(list_filter, list);
    }
}, false);

var list_filter_sort_click_handler = function(ele) {
    // will sort the list based on specified attribute
    // the element will be a button, placed as a child in a list-filter span
    // list will always be the next element/sibling of the parent
    
    // get list elements
    let list = this.parentNode.nextSibling;
    let children = list.querySelectorAll('li');
    let sorting_variable = this.getAttribute('data-for');
    let items_sort_list = [] ;
    for (let node of children) {
        let key = node.getAttribute(sorting_variable);
        if (!isNaN(key)) {
            key = parseInt(key);
        }
        items_sort_list.push({
            key: key,
            value: node}) ;
    }

    // sort list using key and direction
    let sort_direction = this.getAttribute('data-sort-direction');
    if (sort_direction == "asc") {
        items_sort_list.sort(function(a, b) { return a.key > b.key ? 1 : -1; });
        this.setAttribute('data-sort-direction', 'dsc');
    } else if (sort_direction == "dsc") {
        items_sort_list.sort(function(a, b) { return a.key < b.key ? 1 : -1; });
        this.setAttribute('data-sort-direction', 'asc');
    }

    // replace old list with new
    for (let item of items_sort_list) {
        list.appendChild(item.value);
    }
}