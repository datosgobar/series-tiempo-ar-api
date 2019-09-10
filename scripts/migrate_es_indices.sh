#!/usr/bin/env bash

NEW_MAPPING='
{
"mappings" : {
  "doc" : {
    "dynamic" : "strict",
    "_all" : {
      "enabled" : false
    },
    "properties" : {
      "aggregation" : {
        "type" : "keyword"
      },
      "catalog" : {
        "type" : "keyword"
      },
      "change" : {
        "type" : "scaled_float",
        "scaling_factor" : 1.0E7
      },
      "change_a_year_ago" : {
        "type" : "scaled_float",
        "scaling_factor" : 1.0E7
      },
      "interval" : {
        "type" : "keyword"
      },
      "percent_change" : {
        "type" : "scaled_float",
        "scaling_factor" : 1.0E7
      },
      "percent_change_a_year_ago" : {
        "type" : "scaled_float",
        "scaling_factor" : 1.0E7
      },
      "change_since_beginning_of_year": {
        "type" : "scaled_float",
        "scaling_factor" : 1.0E7
      },
      "percent_change_since_beginning_of_year": {
        "type" : "scaled_float",
        "scaling_factor" : 1.0E7
      },
      "raw_value" : {
        "type" : "boolean"
      },
      "series_id" : {
        "type" : "keyword"
      },
      "timestamp" : {
        "type" : "date"
      },
      "value" : {
        "type" : "scaled_float",
        "scaling_factor" : 1.0E7
      }
    }
  }
}
}
'

TMP_INDEX="indicators_tmp"

curl $ES_URL/${TMP_INDEX}/ -XPUT -d"${NEW_MAPPING}"

REINDEX='{
    "source": {"index": "indicators"},
    "dest": {"index": "'${TMP_INDEX}'"}
}';

echo $REINDEX
curl ${ES_URL}/_reindex/ -XPOST -d"${REINDEX}";

curl ${ES_URL}/indicators/ -XDELETE

curl $ES_URL/indicators/ -XPUT -d"${NEW_MAPPING}"

REVERSE_REINDEX='{
    "source": {"index": "'${TMP_INDEX}'"},
    "dest": {"index": "indicators"}
}';

echo $REVERSE_REINDEX

curl $ES_URL/_reindex -XPOST -d"${REVERSE_REINDEX}";