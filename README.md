# Query the TimeCamp API
## This repository aims to show how quick and easy it can be to interact with the TimeCamp API using `pyttimecamp`

This package can be installed through with pip:
```
pip install pytimecamp
```

Something that the orginal package lacked was the ability to query the project name. I reached out to the maintainers of this package but did not hear from them. So I took matters in my own hands and forked their repo, upgraded their code and intstalled my forked version of this package which you can use too:

```
pip install -e git+https://github.com/caspercrause/pytimecamp/#egg=pytimecamp
```

With that installed it's time to look at an example pipeline that I am going to be building with the help of the [dlt](https://dlthub.com/docs/getting-started) package.

`dlt` is an open-source library that you can add to your Python scripts to load data from various and often messy data sources into well-structured, live datasets. 

For dlt to work, make sure you are using Python 3.8-3.11 and have pip installed

Check that by doing:
```
python --version
pip --version
```

With the right version of python on your machine let's whip up a virtual environment:

```
python -m venv ./env
```

Activate it by running:

```
source ./env/bin/activate
```

Install necessary packages for this tutorial:
```
pip install -r requirements.txt
```

To run this example you will need to have a timecamp account as well as an API key:

To fetch that API key check out [this](https://www.make.com/en/help/app/timecamp) documentation


With all of that finally done we are ready to excecute the example:

```
python timecamp.py
```

That will yield an output similar to the following:

```>>> Executing script at Saturday Feb 17, 2024 at 11:09:28
>>> Pipeline test load step completed in 0.63 seconds
>>> 1 load package(s) were loaded to destination duckdb and into dataset timecamp_data
>>> The duckdb destination used duckdb:/Users/caspercrause/Documents/Data-Engineering/test.duckdb location to store data
>>> Load package 1708160969.5296462 is LOADED and contains no failed jobs
```
Since I've called this particular pipeline `timecamp` I can run the following to explore the data and allow a sneak peek and basic discovery you can take advantage of built-in integration with Strealmit:

```
dlt pipeline timecamp show
```
That will open up an interactive window that looks like this:

[![Preview](https://github.com/caspercrause/TimeCamp-Tutorial/blob/master/preview.png)](https://github.com/caspercrause/TimeCamp-Tutorial/blob/master/preview.png)

You can see your total hours for a particular week:

[![Week](https://github.com/caspercrause/TimeCamp-Tutorial/blob/master/total_hours.png)](https://github.com/caspercrause/TimeCamp-Tutorial/blob/master/total_hours.png)


From here you can query your data using normal SQL like queries.

```
SELECT 
    CASE 
        WHEN project_name LIKE '%Communication%' THEN 'Communication'
        WHEN project_name LIKE '%Client%' THEN 'Client Requests'
        WHEN project_name LIKE '%Team%' THEN 'Meetings'
        WHEN project_name LIKE '%Toolbox%' THEN 'Script Development'
        ELSE 'Unknown'
    END AS project_name,
    SUM(duration)/3600 AS hours_worked
FROM 
    daily_table
WHERE 
    user_name ='Casper Crause'
    AND date BETWEEN '2024-01-15' AND '2024-01-19'
GROUP BY 
    project_name;

```

[![Grouped](https://github.com/caspercrause/TimeCamp-Tutorial/blob/master/grouped_by_project.png)](https://github.com/caspercrause/TimeCamp-Tutorial/blob/master/grouped_by_project.png)

In the [script](https://github.com/caspercrause/TimeCamp-Tutorial/blob/master/timecamp.py) there is a final code block:

```
load_info = pipeline.run(
    data,
    write_disposition="merge", 
    primary_key='Entry_id',
    table_name="daily_table"
)
```

The amazing thing about `dlt` is its ability to upsert rows. The script above finds new entries and adds them to the database. While updating existing rows, shoud it detect a change. Thanks to the `write_disposition="merge"` This drastically decrases the amount data-engineers spend on working with data and enables you to spend more time on things that matter... Data Quality!
