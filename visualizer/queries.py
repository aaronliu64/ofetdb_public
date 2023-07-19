# %%
import psycopg2
import pandas as pd
import numpy as np
import plotly.express as px

pgparams = {
    "database": "ofetdb_testenv",
    "user":"postgres",
    "password":"password",
    "host": "127.0.0.1",
    "port": "5432"
    }

def read_select_query(query):

    with psycopg2.connect(**pgparams) as conn:

        df = pd.read_sql_query(query, conn)

    return df

q1 = '''

    SELECT 
    common_name, mn, mw, dispersity,
    solution.concentration,
    CAST (data -> 'hole_mobility' ->> 'value' AS FLOAT) AS hole_mobility,
    CAST (data -> 'electron_mobility' ->> 'value' AS FLOAT) AS electron_mobility
    
    FROM 
    measurement, 
    sample, 
    solution NATURAL JOIN solution_makeup_polymer NATURAL JOIN polymer,
    ofet_process
    
    WHERE
    measurement_type = 'transfer_curve' AND
    measurement.sample_id = sample.sample_id AND
    sample.process_id = ofet_process.process_id AND
    ofet_process.solution_id = solution.solution_id AND 
    wt_frac = 1

    '''        

df_1 = read_select_query(q1)

# q2 = '''
#     SELECT polymer_name, mw_kda, COUNT(*) FROM device, solution, polymer
#     WHERE device.solution_id = solution.solution_id
#     AND solution.polymer_id = polymer.polymer_id
#     GROUP BY polymer_name, mw_kda;
#     '''        

# df_2 = read_select_query(q2)

# # q3 = '''
# #     SELECT polymer_name, solvent.solvent_name, boiling_point_c, min(concentration_mgml)	
# #         AS min_concentration, max(concentration_mgml) AS max_concentration, count(*) AS num_expts
# #     FROM device, solution, solvent, polymer
# #     WHERE device.solution_id = solution.solution_id AND
# #     solution.solvent_name = solvent.solvent_name AND
# #     solution.polymer_id = polymer.polymer_id
# #     GROUP BY solvent.solvent_name, polymer_name
# #     ORDER BY polymer_name
# #     '''     

# # df_3 = read_select_query(q3)

# def q3_mod(polymer_name):
#     query = '''
#     SELECT solvent.solvent_name, boiling_point_c, min(concentration_mgml)	
#         AS min_concentration, max(concentration_mgml) AS max_concentration, count(*) AS num_expts
#     FROM device, solution, solvent, polymer
#     WHERE device.solution_id = solution.solution_id AND
#     solution.solvent_name = solvent.solvent_name AND
#     solution.polymer_id = polymer.polymer_id AND
#     polymer.polymer_name = '%s'
#     GROUP BY solvent.solvent_name, polymer_name
#     ORDER BY polymer_name
#     ''' % polymer_name

#     df_3 = read_select_query(query)

#     return df_3

# q4 = '''
#     SELECT polymer_name, mobility_cm2_vs, deposition_method 
#     FROM device, solution, polymer, coating_process
#     WHERE device.coating_id = coating_process.coating_id AND 
#     device.solution_id = solution.solution_id AND 
#     solution.polymer_id = polymer.polymer_id;
#     '''

# df_4 = read_select_query(q4)

# print("Success")

# # cur = conn.cursor()


# # conn.commit()
# # print("Operation successful")
# # conn.close()
# # %%
# fig4 = px.box(df_4, 
#     x="deposition_method", 
#     y="mobility_cm2_vs", 
#     color="polymer_name", 
#     points="all",
#     log_y=True
#     )
# fig4.show()
# %%
