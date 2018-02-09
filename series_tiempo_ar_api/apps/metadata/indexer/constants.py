#! coding: utf-8

from ..constants import FIELDS_INDEX, FIELDS_DOC_TYPE

FIELDS_MAPPING = """
{
  "mappings": {
    "doc": {
      "properties": {
        "description": {"type": "text"},
        "id": {"type": "keyword"},
        "title": {"type": "keyword"},
        "dataset_title": {"type": "text"},
        "dataset_description": {"type": "text"},
        "dataset_source": {"type": "text"},
        "theme_description": {"type": "text"}
      }
    }
  }
}
"""
