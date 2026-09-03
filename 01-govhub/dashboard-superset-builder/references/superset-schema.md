# Schema do Superset por `viz_type`

Cache estático do schema real de `generate_chart`, obtido via `get_chart_type_schema` do MCP do Superset (serviço `Superset MCP Service`, versão 6.1.0, capturado em 2026-09-03). Evita depender de uma chamada ao vivo ao MCP durante o planejamento (Fases 0–3 da skill); a criação real (Fase 4) ainda pode consultar o MCP ao vivo para um `viz_type` que não esteja aqui.

Como usar: cada bloco abaixo é o retorno bruto de `get_chart_type_schema(chart_type=<tipo>, include_examples=true)`. O objeto sob `schema` é o JSON Schema do config do chart; na Fase 4 esse config vai dentro do parâmetro `request` de `generate_chart`, com `save_chart=true` para persistir (sem isso o `generate_chart` só devolve um preview). Alguns `$defs` se repetem entre os tipos: `ColumnRef` e `FilterConfig` aparecem em todos os 7; `AxisConfig` só em `xy` e `mixed_timeseries`; `TimeGrain` em `xy`, `mixed_timeseries` e `big_number`; `LegendConfig` só em `xy` (os demais usam um booleano `show_legend`). `ColumnRef` é como toda métrica/dimensão é declarada (`name` obrigatório; `aggregate` para métrica ad-hoc; `saved_metric: true` para usar uma métrica salva do dataset). Filtros são sempre estruturados (`column`/`op`/`value`) — nunca `adhoc_filters` nem SQL cru.

## Tipos válidos (`viz_type`)

Lista completa aceita por `get_chart_type_schema` / `generate_chart` (obtida chamando com um `chart_type` inválido):

- `big_number`
- `handlebars`
- `mixed_timeseries`
- `pie`
- `pivot_table`
- `table`
- `xy`

Campos obrigatórios por tipo (o resto tem default no schema):

- `xy`: `x`, `y`
- `table`: `columns`
- `pie`: `dimension`, `metric`
- `pivot_table`: `rows`, `metrics`
- `mixed_timeseries`: `x`, `y`, `y_secondary`
- `big_number`: `chart_type`, `metric`
- `handlebars`: `chart_type`, `handlebars_template`

## xy — linha / barra / área / dispersão

```json
{
  "$defs": {
    "AxisConfig": {
      "properties": {
        "title": {
          "anyOf": [
            {
              "maxLength": 200,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Title"
        },
        "scale": {
          "anyOf": [
            {
              "enum": [
                "linear",
                "log"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": "linear",
          "title": "Scale"
        },
        "format": {
          "anyOf": [
            {
              "maxLength": 50,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "e.g. '$,.2f'",
          "title": "Format"
        }
      },
      "title": "AxisConfig",
      "type": "object"
    },
    "ColumnRef": {
      "properties": {
        "name": {
          "maxLength": 255,
          "minLength": 1,
          "pattern": "^[a-zA-Z0-9_][a-zA-Z0-9_\\s\\-\\.]*$",
          "title": "Name",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "maxLength": 500,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "dtype": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Dtype"
        },
        "aggregate": {
          "anyOf": [
            {
              "enum": [
                "SUM",
                "COUNT",
                "AVG",
                "MIN",
                "MAX",
                "COUNT_DISTINCT",
                "STDDEV",
                "VAR",
                "MEDIAN",
                "PERCENTILE"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "SQL aggregate function",
          "title": "Aggregate"
        },
        "saved_metric": {
          "default": false,
          "description": "If true, 'name' refers to a saved metric from the dataset (use get_dataset_info to see available metrics). When set, 'aggregate' is ignored.",
          "title": "Saved Metric",
          "type": "boolean"
        }
      },
      "required": [
        "name"
      ],
      "title": "ColumnRef",
      "type": "object"
    },
    "FilterConfig": {
      "properties": {
        "column": {
          "maxLength": 255,
          "minLength": 1,
          "pattern": "^[a-zA-Z0-9_][a-zA-Z0-9_\\s\\-\\.]*$",
          "title": "Column",
          "type": "string"
        },
        "op": {
          "description": "LIKE/ILIKE use % wildcards. IN/NOT IN take a list.",
          "enum": [
            "=",
            ">",
            "<",
            ">=",
            "<=",
            "!=",
            "LIKE",
            "ILIKE",
            "NOT LIKE",
            "IN",
            "NOT IN"
          ],
          "title": "Op",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "integer"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "integer"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            }
          ],
          "description": "For IN/NOT IN, provide a list.",
          "title": "Value"
        }
      },
      "required": [
        "column",
        "op",
        "value"
      ],
      "title": "FilterConfig",
      "type": "object"
    },
    "LegendConfig": {
      "properties": {
        "show": {
          "default": true,
          "title": "Show",
          "type": "boolean"
        },
        "position": {
          "anyOf": [
            {
              "enum": [
                "top",
                "bottom",
                "left",
                "right"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": "right",
          "title": "Position"
        }
      },
      "title": "LegendConfig",
      "type": "object"
    },
    "TimeGrain": {
      "enum": [
        "PT1S",
        "PT5S",
        "PT30S",
        "PT1M",
        "PT5M",
        "PT10M",
        "PT15M",
        "PT30M",
        "PT0.5H",
        "PT1H",
        "PT6H",
        "P1D",
        "P1W",
        "1969-12-28T00:00:00Z/P1W",
        "1969-12-29T00:00:00Z/P1W",
        "P1W/1970-01-03T00:00:00Z",
        "P1W/1970-01-04T00:00:00Z",
        "P1M",
        "P3M",
        "P0.25Y",
        "P1Y"
      ],
      "title": "TimeGrain",
      "type": "string"
    }
  },
  "properties": {
    "chart_type": {
      "const": "xy",
      "default": "xy",
      "title": "Chart Type",
      "type": "string"
    },
    "x": {
      "$ref": "#/$defs/ColumnRef",
      "description": "X-axis column"
    },
    "y": {
      "description": "Y-axis metrics (unique labels)",
      "items": {
        "$ref": "#/$defs/ColumnRef"
      },
      "minItems": 1,
      "title": "Y",
      "type": "array"
    },
    "kind": {
      "default": "line",
      "enum": [
        "line",
        "bar",
        "area",
        "scatter"
      ],
      "title": "Kind",
      "type": "string"
    },
    "time_grain": {
      "anyOf": [
        {
          "$ref": "#/$defs/TimeGrain"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "PT1S, PT1M, PT1H, P1D, P1W, P1M, P3M, P1Y"
    },
    "orientation": {
      "anyOf": [
        {
          "enum": [
            "vertical",
            "horizontal"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Bar orientation (only for kind='bar')",
      "title": "Orientation"
    },
    "stacked": {
      "default": false,
      "title": "Stacked",
      "type": "boolean"
    },
    "group_by": {
      "anyOf": [
        {
          "items": {
            "$ref": "#/$defs/ColumnRef"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Series breakdown columns",
      "title": "Group By"
    },
    "x_axis": {
      "anyOf": [
        {
          "$ref": "#/$defs/AxisConfig"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "y_axis": {
      "anyOf": [
        {
          "$ref": "#/$defs/AxisConfig"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "legend": {
      "anyOf": [
        {
          "$ref": "#/$defs/LegendConfig"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "filters": {
      "anyOf": [
        {
          "items": {
            "$ref": "#/$defs/FilterConfig"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Structured filters (column/op/value). Do NOT use adhoc_filters or raw SQL expressions.",
      "title": "Filters"
    },
    "row_limit": {
      "default": 10000,
      "description": "Max data points",
      "maximum": 50000,
      "minimum": 1,
      "title": "Row Limit",
      "type": "integer"
    }
  },
  "required": [
    "x",
    "y"
  ],
  "title": "XYChartConfig",
  "type": "object"
}
```

Exemplo(s) (`include_examples=true`):

```json
[
  {
    "chart_type": "xy",
    "kind": "line",
    "x": {
      "name": "order_date"
    },
    "y": [
      {
        "name": "revenue",
        "aggregate": "SUM"
      }
    ],
    "time_grain": "P1D"
  },
  {
    "chart_type": "xy",
    "kind": "bar",
    "x": {
      "name": "category"
    },
    "y": [
      {
        "name": "sales",
        "aggregate": "SUM"
      }
    ]
  }
]
```

## table — tabela

```json
{
  "$defs": {
    "ColumnRef": {
      "properties": {
        "name": {
          "maxLength": 255,
          "minLength": 1,
          "pattern": "^[a-zA-Z0-9_][a-zA-Z0-9_\\s\\-\\.]*$",
          "title": "Name",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "maxLength": 500,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "dtype": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Dtype"
        },
        "aggregate": {
          "anyOf": [
            {
              "enum": [
                "SUM",
                "COUNT",
                "AVG",
                "MIN",
                "MAX",
                "COUNT_DISTINCT",
                "STDDEV",
                "VAR",
                "MEDIAN",
                "PERCENTILE"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "SQL aggregate function",
          "title": "Aggregate"
        },
        "saved_metric": {
          "default": false,
          "description": "If true, 'name' refers to a saved metric from the dataset (use get_dataset_info to see available metrics). When set, 'aggregate' is ignored.",
          "title": "Saved Metric",
          "type": "boolean"
        }
      },
      "required": [
        "name"
      ],
      "title": "ColumnRef",
      "type": "object"
    },
    "FilterConfig": {
      "properties": {
        "column": {
          "maxLength": 255,
          "minLength": 1,
          "pattern": "^[a-zA-Z0-9_][a-zA-Z0-9_\\s\\-\\.]*$",
          "title": "Column",
          "type": "string"
        },
        "op": {
          "description": "LIKE/ILIKE use % wildcards. IN/NOT IN take a list.",
          "enum": [
            "=",
            ">",
            "<",
            ">=",
            "<=",
            "!=",
            "LIKE",
            "ILIKE",
            "NOT LIKE",
            "IN",
            "NOT IN"
          ],
          "title": "Op",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "integer"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "integer"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            }
          ],
          "description": "For IN/NOT IN, provide a list.",
          "title": "Value"
        }
      },
      "required": [
        "column",
        "op",
        "value"
      ],
      "title": "FilterConfig",
      "type": "object"
    }
  },
  "properties": {
    "chart_type": {
      "const": "table",
      "default": "table",
      "title": "Chart Type",
      "type": "string"
    },
    "viz_type": {
      "default": "table",
      "description": "'ag-grid-table' for interactive features",
      "enum": [
        "table",
        "ag-grid-table"
      ],
      "title": "Viz Type",
      "type": "string"
    },
    "query_mode": {
      "anyOf": [
        {
          "enum": [
            "aggregate",
            "raw"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Query mode: 'raw' returns individual rows without aggregation, 'aggregate' groups data using metrics. When set to 'raw', all columns are treated as plain columns regardless of any aggregate settings. Defaults to auto-detection: 'raw' if no column has an aggregate function, 'aggregate' otherwise.",
      "title": "Query Mode"
    },
    "columns": {
      "description": "Columns with unique labels",
      "items": {
        "$ref": "#/$defs/ColumnRef"
      },
      "minItems": 1,
      "title": "Columns",
      "type": "array"
    },
    "filters": {
      "anyOf": [
        {
          "items": {
            "$ref": "#/$defs/FilterConfig"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Structured filters (column/op/value). Do NOT use adhoc_filters or raw SQL expressions.",
      "title": "Filters"
    },
    "sort_by": {
      "anyOf": [
        {
          "items": {
            "type": "string"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Sort By"
    },
    "row_limit": {
      "default": 1000,
      "description": "Max rows returned",
      "maximum": 50000,
      "minimum": 1,
      "title": "Row Limit",
      "type": "integer"
    }
  },
  "required": [
    "columns"
  ],
  "title": "TableChartConfig",
  "type": "object"
}
```

Exemplo(s) (`include_examples=true`):

```json
[
  {
    "chart_type": "table",
    "columns": [
      {
        "name": "customer_name"
      },
      {
        "name": "revenue",
        "aggregate": "SUM"
      }
    ]
  }
]
```

## pie — pizza / rosca

```json
{
  "$defs": {
    "ColumnRef": {
      "properties": {
        "name": {
          "maxLength": 255,
          "minLength": 1,
          "pattern": "^[a-zA-Z0-9_][a-zA-Z0-9_\\s\\-\\.]*$",
          "title": "Name",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "maxLength": 500,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "dtype": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Dtype"
        },
        "aggregate": {
          "anyOf": [
            {
              "enum": [
                "SUM",
                "COUNT",
                "AVG",
                "MIN",
                "MAX",
                "COUNT_DISTINCT",
                "STDDEV",
                "VAR",
                "MEDIAN",
                "PERCENTILE"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "SQL aggregate function",
          "title": "Aggregate"
        },
        "saved_metric": {
          "default": false,
          "description": "If true, 'name' refers to a saved metric from the dataset (use get_dataset_info to see available metrics). When set, 'aggregate' is ignored.",
          "title": "Saved Metric",
          "type": "boolean"
        }
      },
      "required": [
        "name"
      ],
      "title": "ColumnRef",
      "type": "object"
    },
    "FilterConfig": {
      "properties": {
        "column": {
          "maxLength": 255,
          "minLength": 1,
          "pattern": "^[a-zA-Z0-9_][a-zA-Z0-9_\\s\\-\\.]*$",
          "title": "Column",
          "type": "string"
        },
        "op": {
          "description": "LIKE/ILIKE use % wildcards. IN/NOT IN take a list.",
          "enum": [
            "=",
            ">",
            "<",
            ">=",
            "<=",
            "!=",
            "LIKE",
            "ILIKE",
            "NOT LIKE",
            "IN",
            "NOT IN"
          ],
          "title": "Op",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "integer"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "integer"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            }
          ],
          "description": "For IN/NOT IN, provide a list.",
          "title": "Value"
        }
      },
      "required": [
        "column",
        "op",
        "value"
      ],
      "title": "FilterConfig",
      "type": "object"
    }
  },
  "properties": {
    "chart_type": {
      "const": "pie",
      "default": "pie",
      "title": "Chart Type",
      "type": "string"
    },
    "dimension": {
      "$ref": "#/$defs/ColumnRef",
      "description": "Category column for slices"
    },
    "metric": {
      "$ref": "#/$defs/ColumnRef",
      "description": "Value metric (use aggregate e.g. SUM, COUNT for ad-hoc, or set saved_metric=True for a saved dataset metric)"
    },
    "donut": {
      "default": false,
      "title": "Donut",
      "type": "boolean"
    },
    "show_labels": {
      "default": true,
      "title": "Show Labels",
      "type": "boolean"
    },
    "label_type": {
      "default": "key_value_percent",
      "enum": [
        "key",
        "value",
        "percent",
        "key_value",
        "key_percent",
        "key_value_percent",
        "value_percent"
      ],
      "title": "Label Type",
      "type": "string"
    },
    "sort_by_metric": {
      "default": true,
      "title": "Sort By Metric",
      "type": "boolean"
    },
    "show_legend": {
      "default": true,
      "title": "Show Legend",
      "type": "boolean"
    },
    "filters": {
      "anyOf": [
        {
          "items": {
            "$ref": "#/$defs/FilterConfig"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Structured filters (column/op/value). Do NOT use adhoc_filters or raw SQL expressions.",
      "title": "Filters"
    },
    "row_limit": {
      "default": 100,
      "description": "Max slices",
      "maximum": 10000,
      "minimum": 1,
      "title": "Row Limit",
      "type": "integer"
    },
    "number_format": {
      "default": "SMART_NUMBER",
      "maxLength": 50,
      "title": "Number Format",
      "type": "string"
    },
    "show_total": {
      "default": false,
      "description": "Show total in center",
      "title": "Show Total",
      "type": "boolean"
    },
    "labels_outside": {
      "default": true,
      "title": "Labels Outside",
      "type": "boolean"
    },
    "outer_radius": {
      "default": 70,
      "description": "Outer radius % (1-100)",
      "maximum": 100,
      "minimum": 1,
      "title": "Outer Radius",
      "type": "integer"
    },
    "inner_radius": {
      "default": 30,
      "description": "Donut inner radius % (1-100)",
      "maximum": 100,
      "minimum": 1,
      "title": "Inner Radius",
      "type": "integer"
    }
  },
  "required": [
    "dimension",
    "metric"
  ],
  "title": "PieChartConfig",
  "type": "object"
}
```

Exemplo(s) (`include_examples=true`):

```json
[
  {
    "chart_type": "pie",
    "dimension": {
      "name": "region"
    },
    "metric": {
      "name": "revenue",
      "aggregate": "SUM"
    }
  }
]
```

## pivot_table — tabela dinâmica

```json
{
  "$defs": {
    "ColumnRef": {
      "properties": {
        "name": {
          "maxLength": 255,
          "minLength": 1,
          "pattern": "^[a-zA-Z0-9_][a-zA-Z0-9_\\s\\-\\.]*$",
          "title": "Name",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "maxLength": 500,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "dtype": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Dtype"
        },
        "aggregate": {
          "anyOf": [
            {
              "enum": [
                "SUM",
                "COUNT",
                "AVG",
                "MIN",
                "MAX",
                "COUNT_DISTINCT",
                "STDDEV",
                "VAR",
                "MEDIAN",
                "PERCENTILE"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "SQL aggregate function",
          "title": "Aggregate"
        },
        "saved_metric": {
          "default": false,
          "description": "If true, 'name' refers to a saved metric from the dataset (use get_dataset_info to see available metrics). When set, 'aggregate' is ignored.",
          "title": "Saved Metric",
          "type": "boolean"
        }
      },
      "required": [
        "name"
      ],
      "title": "ColumnRef",
      "type": "object"
    },
    "FilterConfig": {
      "properties": {
        "column": {
          "maxLength": 255,
          "minLength": 1,
          "pattern": "^[a-zA-Z0-9_][a-zA-Z0-9_\\s\\-\\.]*$",
          "title": "Column",
          "type": "string"
        },
        "op": {
          "description": "LIKE/ILIKE use % wildcards. IN/NOT IN take a list.",
          "enum": [
            "=",
            ">",
            "<",
            ">=",
            "<=",
            "!=",
            "LIKE",
            "ILIKE",
            "NOT LIKE",
            "IN",
            "NOT IN"
          ],
          "title": "Op",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "integer"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "integer"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            }
          ],
          "description": "For IN/NOT IN, provide a list.",
          "title": "Value"
        }
      },
      "required": [
        "column",
        "op",
        "value"
      ],
      "title": "FilterConfig",
      "type": "object"
    }
  },
  "properties": {
    "chart_type": {
      "const": "pivot_table",
      "default": "pivot_table",
      "title": "Chart Type",
      "type": "string"
    },
    "rows": {
      "description": "Row grouping columns",
      "items": {
        "$ref": "#/$defs/ColumnRef"
      },
      "minItems": 1,
      "title": "Rows",
      "type": "array"
    },
    "columns": {
      "anyOf": [
        {
          "items": {
            "$ref": "#/$defs/ColumnRef"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Column groups for cross-tabulation",
      "title": "Columns"
    },
    "metrics": {
      "description": "Metrics (use aggregate e.g. SUM, COUNT, AVG for ad-hoc, or set saved_metric=True for saved dataset metrics)",
      "items": {
        "$ref": "#/$defs/ColumnRef"
      },
      "minItems": 1,
      "title": "Metrics",
      "type": "array"
    },
    "aggregate_function": {
      "default": "Sum",
      "enum": [
        "Sum",
        "Average",
        "Median",
        "Sample Variance",
        "Sample Standard Deviation",
        "Minimum",
        "Maximum",
        "Count",
        "Count Unique Values",
        "First",
        "Last"
      ],
      "title": "Aggregate Function",
      "type": "string"
    },
    "show_row_totals": {
      "default": true,
      "title": "Show Row Totals",
      "type": "boolean"
    },
    "show_column_totals": {
      "default": true,
      "title": "Show Column Totals",
      "type": "boolean"
    },
    "transpose": {
      "default": false,
      "title": "Transpose",
      "type": "boolean"
    },
    "combine_metric": {
      "default": false,
      "description": "Metrics side by side in columns",
      "title": "Combine Metric",
      "type": "boolean"
    },
    "filters": {
      "anyOf": [
        {
          "items": {
            "$ref": "#/$defs/FilterConfig"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Structured filters (column/op/value). Do NOT use adhoc_filters or raw SQL expressions.",
      "title": "Filters"
    },
    "row_limit": {
      "default": 10000,
      "description": "Max cells",
      "maximum": 50000,
      "minimum": 1,
      "title": "Row Limit",
      "type": "integer"
    },
    "value_format": {
      "default": "SMART_NUMBER",
      "maxLength": 50,
      "title": "Value Format",
      "type": "string"
    }
  },
  "required": [
    "rows",
    "metrics"
  ],
  "title": "PivotTableChartConfig",
  "type": "object"
}
```

Exemplo(s) (`include_examples=true`):

```json
[
  {
    "chart_type": "pivot_table",
    "rows": [
      {
        "name": "region"
      }
    ],
    "metrics": [
      {
        "name": "revenue",
        "aggregate": "SUM"
      }
    ],
    "columns": [
      {
        "name": "quarter"
      }
    ]
  }
]
```

## mixed_timeseries — série temporal com eixo Y duplo

```json
{
  "$defs": {
    "AxisConfig": {
      "properties": {
        "title": {
          "anyOf": [
            {
              "maxLength": 200,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Title"
        },
        "scale": {
          "anyOf": [
            {
              "enum": [
                "linear",
                "log"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": "linear",
          "title": "Scale"
        },
        "format": {
          "anyOf": [
            {
              "maxLength": 50,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "e.g. '$,.2f'",
          "title": "Format"
        }
      },
      "title": "AxisConfig",
      "type": "object"
    },
    "ColumnRef": {
      "properties": {
        "name": {
          "maxLength": 255,
          "minLength": 1,
          "pattern": "^[a-zA-Z0-9_][a-zA-Z0-9_\\s\\-\\.]*$",
          "title": "Name",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "maxLength": 500,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "dtype": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Dtype"
        },
        "aggregate": {
          "anyOf": [
            {
              "enum": [
                "SUM",
                "COUNT",
                "AVG",
                "MIN",
                "MAX",
                "COUNT_DISTINCT",
                "STDDEV",
                "VAR",
                "MEDIAN",
                "PERCENTILE"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "SQL aggregate function",
          "title": "Aggregate"
        },
        "saved_metric": {
          "default": false,
          "description": "If true, 'name' refers to a saved metric from the dataset (use get_dataset_info to see available metrics). When set, 'aggregate' is ignored.",
          "title": "Saved Metric",
          "type": "boolean"
        }
      },
      "required": [
        "name"
      ],
      "title": "ColumnRef",
      "type": "object"
    },
    "FilterConfig": {
      "properties": {
        "column": {
          "maxLength": 255,
          "minLength": 1,
          "pattern": "^[a-zA-Z0-9_][a-zA-Z0-9_\\s\\-\\.]*$",
          "title": "Column",
          "type": "string"
        },
        "op": {
          "description": "LIKE/ILIKE use % wildcards. IN/NOT IN take a list.",
          "enum": [
            "=",
            ">",
            "<",
            ">=",
            "<=",
            "!=",
            "LIKE",
            "ILIKE",
            "NOT LIKE",
            "IN",
            "NOT IN"
          ],
          "title": "Op",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "integer"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "integer"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            }
          ],
          "description": "For IN/NOT IN, provide a list.",
          "title": "Value"
        }
      },
      "required": [
        "column",
        "op",
        "value"
      ],
      "title": "FilterConfig",
      "type": "object"
    },
    "TimeGrain": {
      "enum": [
        "PT1S",
        "PT5S",
        "PT30S",
        "PT1M",
        "PT5M",
        "PT10M",
        "PT15M",
        "PT30M",
        "PT0.5H",
        "PT1H",
        "PT6H",
        "P1D",
        "P1W",
        "1969-12-28T00:00:00Z/P1W",
        "1969-12-29T00:00:00Z/P1W",
        "P1W/1970-01-03T00:00:00Z",
        "P1W/1970-01-04T00:00:00Z",
        "P1M",
        "P3M",
        "P0.25Y",
        "P1Y"
      ],
      "title": "TimeGrain",
      "type": "string"
    }
  },
  "properties": {
    "chart_type": {
      "const": "mixed_timeseries",
      "default": "mixed_timeseries",
      "title": "Chart Type",
      "type": "string"
    },
    "x": {
      "$ref": "#/$defs/ColumnRef",
      "description": "Shared temporal X-axis column"
    },
    "time_grain": {
      "anyOf": [
        {
          "$ref": "#/$defs/TimeGrain"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "PT1H, P1D, P1W, P1M, P1Y"
    },
    "y": {
      "description": "Primary Y-axis metrics",
      "items": {
        "$ref": "#/$defs/ColumnRef"
      },
      "minItems": 1,
      "title": "Y",
      "type": "array"
    },
    "primary_kind": {
      "default": "line",
      "enum": [
        "line",
        "bar",
        "area",
        "scatter"
      ],
      "title": "Primary Kind",
      "type": "string"
    },
    "group_by": {
      "anyOf": [
        {
          "items": {
            "$ref": "#/$defs/ColumnRef"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Primary series group by",
      "title": "Group By"
    },
    "y_secondary": {
      "description": "Secondary Y-axis metrics",
      "items": {
        "$ref": "#/$defs/ColumnRef"
      },
      "minItems": 1,
      "title": "Y Secondary",
      "type": "array"
    },
    "secondary_kind": {
      "default": "bar",
      "enum": [
        "line",
        "bar",
        "area",
        "scatter"
      ],
      "title": "Secondary Kind",
      "type": "string"
    },
    "group_by_secondary": {
      "anyOf": [
        {
          "items": {
            "$ref": "#/$defs/ColumnRef"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Secondary series group by",
      "title": "Group By Secondary"
    },
    "show_legend": {
      "default": true,
      "title": "Show Legend",
      "type": "boolean"
    },
    "x_axis": {
      "anyOf": [
        {
          "$ref": "#/$defs/AxisConfig"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "y_axis": {
      "anyOf": [
        {
          "$ref": "#/$defs/AxisConfig"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "y_axis_secondary": {
      "anyOf": [
        {
          "$ref": "#/$defs/AxisConfig"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "filters": {
      "anyOf": [
        {
          "items": {
            "$ref": "#/$defs/FilterConfig"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Structured filters (column/op/value). Do NOT use adhoc_filters or raw SQL expressions.",
      "title": "Filters"
    },
    "row_limit": {
      "default": 10000,
      "description": "Max data points",
      "maximum": 50000,
      "minimum": 1,
      "title": "Row Limit",
      "type": "integer"
    }
  },
  "required": [
    "x",
    "y",
    "y_secondary"
  ],
  "title": "MixedTimeseriesChartConfig",
  "type": "object"
}
```

Exemplo(s) (`include_examples=true`):

```json
[
  {
    "chart_type": "mixed_timeseries",
    "x": {
      "name": "order_date"
    },
    "y": [
      {
        "name": "revenue",
        "aggregate": "SUM"
      }
    ],
    "y_secondary": [
      {
        "name": "orders",
        "aggregate": "COUNT"
      }
    ],
    "time_grain": "P1M"
  }
]
```

## big_number — KPI / big number

```json
{
  "$defs": {
    "ColumnRef": {
      "properties": {
        "name": {
          "maxLength": 255,
          "minLength": 1,
          "pattern": "^[a-zA-Z0-9_][a-zA-Z0-9_\\s\\-\\.]*$",
          "title": "Name",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "maxLength": 500,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "dtype": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Dtype"
        },
        "aggregate": {
          "anyOf": [
            {
              "enum": [
                "SUM",
                "COUNT",
                "AVG",
                "MIN",
                "MAX",
                "COUNT_DISTINCT",
                "STDDEV",
                "VAR",
                "MEDIAN",
                "PERCENTILE"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "SQL aggregate function",
          "title": "Aggregate"
        },
        "saved_metric": {
          "default": false,
          "description": "If true, 'name' refers to a saved metric from the dataset (use get_dataset_info to see available metrics). When set, 'aggregate' is ignored.",
          "title": "Saved Metric",
          "type": "boolean"
        }
      },
      "required": [
        "name"
      ],
      "title": "ColumnRef",
      "type": "object"
    },
    "FilterConfig": {
      "properties": {
        "column": {
          "maxLength": 255,
          "minLength": 1,
          "pattern": "^[a-zA-Z0-9_][a-zA-Z0-9_\\s\\-\\.]*$",
          "title": "Column",
          "type": "string"
        },
        "op": {
          "description": "LIKE/ILIKE use % wildcards. IN/NOT IN take a list.",
          "enum": [
            "=",
            ">",
            "<",
            ">=",
            "<=",
            "!=",
            "LIKE",
            "ILIKE",
            "NOT LIKE",
            "IN",
            "NOT IN"
          ],
          "title": "Op",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "integer"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "integer"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            }
          ],
          "description": "For IN/NOT IN, provide a list.",
          "title": "Value"
        }
      },
      "required": [
        "column",
        "op",
        "value"
      ],
      "title": "FilterConfig",
      "type": "object"
    },
    "TimeGrain": {
      "enum": [
        "PT1S",
        "PT5S",
        "PT30S",
        "PT1M",
        "PT5M",
        "PT10M",
        "PT15M",
        "PT30M",
        "PT0.5H",
        "PT1H",
        "PT6H",
        "P1D",
        "P1W",
        "1969-12-28T00:00:00Z/P1W",
        "1969-12-29T00:00:00Z/P1W",
        "P1W/1970-01-03T00:00:00Z",
        "P1W/1970-01-04T00:00:00Z",
        "P1M",
        "P3M",
        "P0.25Y",
        "P1Y"
      ],
      "title": "TimeGrain",
      "type": "string"
    }
  },
  "properties": {
    "chart_type": {
      "const": "big_number",
      "description": "Chart type discriminator - MUST be 'big_number'. Creates Big Number charts that display a single prominent metric value. Set show_trendline=True with a temporal_column for a number with trendline, or leave show_trendline=False for a standalone number.",
      "title": "Chart Type",
      "type": "string"
    },
    "metric": {
      "$ref": "#/$defs/ColumnRef",
      "description": "The metric to display as a big number. Must include an aggregate function (e.g., SUM, COUNT)."
    },
    "temporal_column": {
      "anyOf": [
        {
          "maxLength": 255,
          "minLength": 1,
          "pattern": "^[a-zA-Z0-9_][a-zA-Z0-9_\\s\\-\\.]*$",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Temporal column for the trendline x-axis. Required when show_trendline is True.",
      "title": "Temporal Column"
    },
    "time_grain": {
      "anyOf": [
        {
          "$ref": "#/$defs/TimeGrain"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Time granularity for trendline data. Common values: PT1H (hour), P1D (day), P1W (week), P1M (month), P1Y (year)."
    },
    "show_trendline": {
      "default": false,
      "description": "Show a trendline below the big number. Requires 'temporal_column' to be set.",
      "title": "Show Trendline",
      "type": "boolean"
    },
    "subheader": {
      "anyOf": [
        {
          "maxLength": 500,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Subtitle text displayed below the big number",
      "title": "Subheader"
    },
    "y_axis_format": {
      "anyOf": [
        {
          "maxLength": 50,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Number format string for the metric value (e.g., '$,.2f' for currency, ',.0f' for integers, '.2%' for percentages)",
      "title": "Y Axis Format"
    },
    "start_y_axis_at_zero": {
      "default": true,
      "description": "Anchor trendline y-axis at zero",
      "title": "Start Y Axis At Zero",
      "type": "boolean"
    },
    "compare_lag": {
      "anyOf": [
        {
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Number of time periods to compare against. Displays a percentage change vs the prior period.",
      "title": "Compare Lag"
    },
    "filters": {
      "anyOf": [
        {
          "items": {
            "$ref": "#/$defs/FilterConfig"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Filters to apply",
      "title": "Filters"
    }
  },
  "required": [
    "chart_type",
    "metric"
  ],
  "title": "BigNumberChartConfig",
  "type": "object"
}
```

Exemplo(s) (`include_examples=true`):

```json
[
  {
    "chart_type": "big_number",
    "metric": {
      "name": "revenue",
      "aggregate": "SUM"
    }
  }
]
```

## handlebars — template HTML customizado (cards de KPI, leaderboards)

```json
{
  "$defs": {
    "ColumnRef": {
      "properties": {
        "name": {
          "maxLength": 255,
          "minLength": 1,
          "pattern": "^[a-zA-Z0-9_][a-zA-Z0-9_\\s\\-\\.]*$",
          "title": "Name",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "maxLength": 500,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "dtype": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Dtype"
        },
        "aggregate": {
          "anyOf": [
            {
              "enum": [
                "SUM",
                "COUNT",
                "AVG",
                "MIN",
                "MAX",
                "COUNT_DISTINCT",
                "STDDEV",
                "VAR",
                "MEDIAN",
                "PERCENTILE"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "SQL aggregate function",
          "title": "Aggregate"
        },
        "saved_metric": {
          "default": false,
          "description": "If true, 'name' refers to a saved metric from the dataset (use get_dataset_info to see available metrics). When set, 'aggregate' is ignored.",
          "title": "Saved Metric",
          "type": "boolean"
        }
      },
      "required": [
        "name"
      ],
      "title": "ColumnRef",
      "type": "object"
    },
    "FilterConfig": {
      "properties": {
        "column": {
          "maxLength": 255,
          "minLength": 1,
          "pattern": "^[a-zA-Z0-9_][a-zA-Z0-9_\\s\\-\\.]*$",
          "title": "Column",
          "type": "string"
        },
        "op": {
          "description": "LIKE/ILIKE use % wildcards. IN/NOT IN take a list.",
          "enum": [
            "=",
            ">",
            "<",
            ">=",
            "<=",
            "!=",
            "LIKE",
            "ILIKE",
            "NOT LIKE",
            "IN",
            "NOT IN"
          ],
          "title": "Op",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "integer"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "integer"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            }
          ],
          "description": "For IN/NOT IN, provide a list.",
          "title": "Value"
        }
      },
      "required": [
        "column",
        "op",
        "value"
      ],
      "title": "FilterConfig",
      "type": "object"
    }
  },
  "properties": {
    "chart_type": {
      "const": "handlebars",
      "description": "Chart type discriminator - MUST be 'handlebars' for custom HTML template charts. Handlebars charts render query results using Handlebars templates, enabling fully custom layouts like KPI cards, leaderboards, and formatted reports.",
      "title": "Chart Type",
      "type": "string"
    },
    "handlebars_template": {
      "description": "Handlebars HTML template string. Data is available as {{data}} array. Built-in helpers: {{dateFormat val format='YYYY-MM-DD'}}, {{formatNumber val}}, {{stringify obj}}. Example: '<ul>{{#each data}}<li>{{this.name}}: {{this.value}}</li>{{/each}}</ul>'",
      "maxLength": 50000,
      "minLength": 1,
      "title": "Handlebars Template",
      "type": "string"
    },
    "query_mode": {
      "default": "aggregate",
      "description": "Query mode: 'aggregate' groups data with metrics, 'raw' returns individual rows",
      "enum": [
        "aggregate",
        "raw"
      ],
      "title": "Query Mode",
      "type": "string"
    },
    "columns": {
      "anyOf": [
        {
          "items": {
            "$ref": "#/$defs/ColumnRef"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Columns to display in raw mode (query_mode='raw'). Each column specifies a column name to include in the query results.",
      "title": "Columns"
    },
    "groupby": {
      "anyOf": [
        {
          "items": {
            "$ref": "#/$defs/ColumnRef"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Columns to group by in aggregate mode (query_mode='aggregate'). These become the dimensions for aggregation.",
      "title": "Groupby"
    },
    "metrics": {
      "anyOf": [
        {
          "items": {
            "$ref": "#/$defs/ColumnRef"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Metrics to aggregate in aggregate mode. Each must have an aggregate function (e.g., SUM, COUNT).",
      "title": "Metrics"
    },
    "filters": {
      "anyOf": [
        {
          "items": {
            "$ref": "#/$defs/FilterConfig"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Filters to apply",
      "title": "Filters"
    },
    "row_limit": {
      "default": 1000,
      "description": "Maximum number of rows",
      "maximum": 50000,
      "minimum": 1,
      "title": "Row Limit",
      "type": "integer"
    },
    "order_desc": {
      "default": true,
      "description": "Sort in descending order",
      "title": "Order Desc",
      "type": "boolean"
    },
    "style_template": {
      "anyOf": [
        {
          "maxLength": 10000,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional CSS styles to apply to the rendered template",
      "title": "Style Template"
    }
  },
  "required": [
    "chart_type",
    "handlebars_template"
  ],
  "title": "HandlebarsChartConfig",
  "type": "object"
}
```

Exemplo(s) (`include_examples=true`):

```json
[
  {
    "chart_type": "handlebars",
    "query_mode": "raw",
    "columns": [
      {
        "name": "customer_name"
      },
      {
        "name": "email"
      }
    ],
    "handlebars_template": "{{#each data}}<p>{{customer_name}}</p>{{/each}}"
  }
]
```

