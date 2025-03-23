# pages.yaml

`pages.yaml` is where you configure the different pages of the control matrix. For a basic explanation of pages see the sub-section of [zcx concepts](/tutorials/getting-started/zcx-concepts/#pages).

## advanced settings

### order

You may define an `order` key in `pages.yaml` to set the order of your pages, rather than moving the entries in the `pages` key.

```yaml
pages:
  page_one:
    - big_section
  page_two:
    - big_section

order:
  - page_one
  - page_two
```

### on_enter, on_leave

You can configure a [command bundle](../command-reference.md) that is executed when the page is entered and/or when the page is left. Doing so requires a slight change to the normal pages syntax:

```yaml
pages:
  page_one:
    sections:
      - actions_left
      - actions_right
    on_enter: METRO
    on_leave:
      msg: >
        left page ${page_number} (${page_name})
```
