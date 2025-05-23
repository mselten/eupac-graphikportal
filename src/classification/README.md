# Prompt

{title}
{objectDescription}
{subject}

I gave you title, description and subjects of painting. 
Based on this information decide what categories does this painting belong to. Choose only from these categories: 
- military 
- spirituality 
- female_representation 
- everyday_life 
- historical_people 
- landscape
You can choose one or more. If none of the categories above apply reply with "other". 
Reply only with list of categories separated by ; no other text should be in reply.
\no_think  



# Prompt to generate code
I have file in file_path = '../../output_csv/bremen_data_V4_translated.csv'

I want you to add new column "custom_category"
You will add this category by calling language model

You will go row by row and if in the row there is text in column "objectDescription" or "subject" then we will do the category otherwise we will leave it empty.

the prompt will look like this:

"""
{title}
{objectDescription}
{subject}

I gave you title, description and subjects of painting.
Based on this information decide what categories does this painting belong to. Choose only from these categories:
- military
- spirituality
- female_representation
- everyday_life
- historical_people
- landscape
  You can choose one or more. If none of the categories above apply reply with "other".
  Reply only with list of categories separated by ; no other text should be in reply.
"""


I want you to do proper output with progress type x/y and other good output so I can see it is working.
I also want to save the result after each 5 answers so that if the program is stopped we can continue.

give me code and prepare dummy function that calls the llm api

save to '../../output_csv/bremen_data_V5_categories.csv'