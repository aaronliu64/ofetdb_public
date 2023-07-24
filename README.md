## ofetdb_public

In support of submitted manuscript:
"Conjugated Polymer Process Ontology and Experimental Data Repository for Organic Field-Effect Transistors"

**Authors**: Aaron L. Liu, Myeongyeon Lee, Rahul Venkatesh, Jessica A. Bonsu, Ron Volkovinsky, J. Carson Meredith,  Elsa Reichmanis, Martha A. Grover

### Instructions:

This file contains instructions on how to add OFET data from a template to the database using the standardized excel template (`Sample_Template.xlsx`)

0. Install Anaconda and PostgreSQL. Clone this repository to your local computer.

1. In pgAdmin or psql, create a new database named `ofetdb_testenv` (or any preferred name). Make sure to save the database information for later use.

2. Create a new virtual environment for ofetdb, and then activate it using:

```
    conda create -n <name_of_env> python=3.11.4
    conda activate <name_of_env>
```

3. Ensure you have the appropriate Python libraries installed:
```
    pip install -r requirements.txt
```
4. Change directory to "create_ofetdb".

    First, run the "create_ofetdb_tables.py", then "import_combined_dataset.py". Ensure that the `kwargs/param_dict` in the scripts contain the correct database connection information, 
such as the database name, user/password, etc., that was used to install PostgreSQL.

```
    python create_ofetdb_tables.py`
    python import_combined_dataset.py`
```

5. If the execution is successful, you should be able to see populated tables in pgAdmin under your database.


6. Now run the `run_template.ipynb` using Jupyter notebook. Before executing, double-check the file path name for the sample_template and the database connection information to ensure they are correct.
