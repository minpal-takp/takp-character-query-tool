---
# TAKP Character Importer and Query Tool

This Python script fetches character data from the TAKP (The Al'Kabor Project) server, stores it in a local SQLite database, and provides a command-line interface for querying characters based on class, name, and various attributes.

## Features

* Download and import the latest TAKP character data.
* Store character data locally in an SQLite database.
* Query characters by exact name or class.
* Select and sort by various character attributes.
* Tabulated output for easy reading.
  
---

## Requirements

* Python 3.7+
* Required packages:

  * `requests`
  * `tabulate`

You can install the dependencies using:

```bash
pip install requests tabulate
```

---

## Usage

### Basic Command

```bash
python takp_char_tools.py
```

This will:

* Download the character data from TAKP
* Import it into a local SQLite database (`takp_characters.db`)

---

### Query Examples

#### Query top 10 Paladins (default columns):

```bash
python takp_char_tools.py --class paladin
```

#### Query character by exact name:

```bash
python takp_char_tools.py --name Sirblade
```

#### Customize columns:

```bash
python takp_char_tools.py --class ranger --columns name,class,level,guild_name
```

#### Change number of results:

```bash
python takp_char_tools.py --class shadowknight --limit 5
```

#### Sort by a different column (e.g., `mana_max_total`):

```bash
python takp_char_tools.py --class cleric --order-by mana_max_total
```

#### Refresh the character database manually:

```bash
python takp_char_tools.py --refresh-data
```

---

## Command Line Options

| Option              | Description                                                                                           |
| ------------------- | ----------------------------------------------------------------------------------------------------- |
| `--refresh-data`    | Download and import the latest character data. (Also the default action when no arguments used)       |
| `--class CLASSNAME` | Query characters of a specific class (e.g., `Paladin`, `Cleric`).                                     |
| `--name CHARACTER`  | Query by exact character name.                                                                        |
| `--limit N`         | Limit the number of query results. Default is `10`.                                                   |
| `--order-by COLUMN` | Column to sort the results by. Default is `hp_max_total`.                                             |
| `--columns COLS`    | Comma-separated list of columns to display. Defaults to:                                              |
|                     | `name, last_name, guild_name, hp_max_total, mana_max_total, ac_total, hp_regen_item, mana_regen_item` |

---

## Output Example

```bash
python takp_char_tools.py --class bard --limit 3 --order-by mana_max_total
```

```
Querying by class: Bard, ordering by mana_max_total, limit 3...

Results:

+------------+------------+--------------+----------------+----------------+------------+----------------+------------------+
| Name       | Last Name | Guild Name   | Hp Max Total   | Mana Max Total | Ac Total   | Hp Regen Item  | Mana Regen Item  |
+============+============+==============+================+================+============+================+==================+
| Singblade  | Melody    | Echo Hunters | 2450           | 1100           | 450        | 20             | 15               |
| Balladdrin | Songspire | Crescendo    | 2300           | 1075           | 430        | 18             | 14               |
| Lyriessa   | Nightwind | Minstrel's Co| 2250           | 1050           | 420        | 17             | 13               |
+------------+------------+--------------+----------------+----------------+------------+----------------+------------------+
```

---

## Notes

* If both `--class` and `--name` are specified, the script will return an error.
* The list of valid columns is determined dynamically from the data. Invalid column names will be rejected with suggestions.

---

## License

This script is provided "as is" with no warranty. Use at your own risk.
