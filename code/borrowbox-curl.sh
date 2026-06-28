#!/usr/bin/env sh

curl 'https://dublin.borrowbox.com/api/v1/search/products?offset=0&limit=60&availableOnly=false' \
  --compressed \
  -X POST \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:151.0) Gecko/20100101 Firefox/151.0' \
  -H 'Accept: application/json' \
  -H 'Accept-Language: en-GB,en;q=0.9' \
  -H 'Accept-Encoding: gzip, deflate, br, zstd' \
  -H 'Content-Type: application/json' \
  -H 'app-name: ppui' \
  -H 'app-siteId: 4815' \
  -H 'app-language: en-GB' \
  -H 'app-clientIp: <IP>' \
  -H 'app-patronId: ' \
  -H 'X-XSRF-TOKEN: <TOKEN>' \
  -H 'Origin: https://dublin.borrowbox.com' \
  -H 'DNT: 1' \
  -H 'Sec-GPC: 1' \
  -H 'Connection: keep-alive' \
  -H 'Cookie: XSRF-TOKEN=<TOKEN>' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Pragma: no-cache' \
  -H 'Cache-Control: no-cache' \
  -H 'TE: trailers' \
  --data-raw '{"searchOperation":"CONJUNCTION","searchTerm":{"TITLE":"<TITLE>","GENRE":"","SERIES":"","AUTHOR":"<AUTHOR>","NARRATOR":"","ISBN":""},"fuzzy":false,"filters":{"loanFormat":["eBooks"]}}'
