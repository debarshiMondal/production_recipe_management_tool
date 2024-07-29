import pandas as pd
import os
from collections import defaultdict

UPLOAD_FOLDER = 'data/Recipes'
TEMP_FOLDER = 'data/Recipes_tmp'

if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

def scale_recipe(filepath, unit, quantity):
    df = pd.read_excel(filepath)
    scaling_factor = df['Quantity (Gm)'].sum() / quantity  # Correctly calculate the scaling factor

    if unit == 'gm':
        if 'Quantity (Gm)' in df.columns:
            df['Quantity (Gm)'] = df['Quantity (Gm)'] / scaling_factor
        if 'Quantity (Pieces)' in df.columns:
            df['Quantity (Pieces)'] = df['Quantity (Pieces)'] / scaling_factor

    elif unit == 'pieces':
        if 'Quantity (Pieces)' in df.columns:
            df['Quantity (Pieces)'] = df['Quantity (Pieces)'] / scaling_factor
        if 'Quantity (Gm)' in df.columns:
            df['Quantity (Gm)'] = df['Quantity (Gm)'] / scaling_factor

    # Remove Unit Cost and Price columns if they exist
    if 'Unit Cost' in df.columns:
        df.drop(columns=['Unit Cost'], inplace=True)
    if 'Price' in df.columns:
        df.drop(columns=['Price'], inplace=True)

    scaled_filepath = filepath.replace('.xlsx', f'_scaled_{quantity}_{unit}.xlsx')
    df.to_excel(scaled_filepath, index=False)
    return scaled_filepath

def generate_shopping_list(recipes):
    all_ingredients = defaultdict(lambda: {"Quantity (Gm)": 0, "Quantity (Pieces)": 0, "Unit Cost": 0, "Price": 0})
    
    for recipe in recipes:
        filepath = os.path.join(UPLOAD_FOLDER, recipe['filename'])
        df = pd.read_excel(filepath)

        # Calculate the scaling factor based on the original recipe yield
        original_yield = float(recipe['filename'].split('_')[0])  # Extracting original yield from the filename
        scaling_factor = float(recipe['quantity']) / original_yield

        # Scale the quantities
        if 'Quantity (Gm)' in df.columns:
            df['Quantity (Gm)'] = df['Quantity (Gm)'] * scaling_factor
        if 'Quantity (Pieces)' in df.columns:
            df['Quantity (Pieces)'] = df['Quantity (Pieces)'] * scaling_factor
        
        # Save scaled ingredients to temporary files
        scaled_filepath = os.path.join(TEMP_FOLDER, recipe['filename'])
        df.to_excel(scaled_filepath, index=False)
        
        if 'Ingredients' not in df.columns:
            raise KeyError(f"'Ingredients' column is missing in the file: {recipe['filename']}")
        
        for _, row in df.iterrows():
            ingredient = row['Ingredients']
            all_ingredients[ingredient]['Quantity (Gm)'] += row['Quantity (Gm)']
            all_ingredients[ingredient]['Quantity (Pieces)'] += row['Quantity (Pieces)']
            all_ingredients[ingredient]['Unit Cost'] = row['Unit Cost']
            all_ingredients[ingredient]['Price'] += (row['Quantity (Gm)'] * row['Unit Cost'] if row['Quantity (Gm)'] > 0 else row['Quantity (Pieces)'] * row['Unit Cost'])
    
    # Convert the aggregated ingredients to a DataFrame
    data = []
    for ingredient, details in all_ingredients.items():
        data.append([ingredient, details['Quantity (Gm)'], details['Quantity (Pieces)'], details['Unit Cost'], details['Price']])
    
    combined_df = pd.DataFrame(data, columns=["Ingredients", "Quantity (Gm)", "Quantity (Pieces)", "Unit Cost", "Price"])

    # Calculate the total price for all ingredients
    total_price = combined_df['Price'].sum()

    # Add total price row at the bottom
    total_price_row = pd.DataFrame([['Total', '', '', '', total_price]], columns=['Ingredients', 'Quantity (Gm)', 'Quantity (Pieces)', 'Unit Cost', 'Price'])
    combined_df = pd.concat([combined_df, total_price_row])

    return combined_df

def generate_estimation_report(recipes):
    data = []
    for recipe in recipes:
        filename = recipe['filename']
        unit = recipe['unit']
        quantity = float(recipe['quantity'])
        df = pd.read_excel(os.path.join('data/Recipes', filename))
        total_cost = df['Price'].sum() * quantity
        data.append({
            'Recipe Name': filename.rsplit('_', 2)[2],
            'Quantity': quantity,
            'Unit': unit,
            'Total Cost': total_cost
        })
    return pd.DataFrame(data)
