import random
import uuid
import pandas as pd
from datasketch import MinHash, MinHashLSH
import re


"""
E-commerce Recommendation Engines: To maintain "freshness," recommender systems use deduplication 
(often as a re-ranking step) to ensure users aren't repetitively shown products they have already seen or purchased.
In E-commerce, deduplication is less about finding "identical text" and more about Diversity & Freshness Engineering. 
If a user sees 10 nearly identical white t-shirts from different brands, the recommendation 
engine has failed to provide a meaningful choice.

How Deduplication works in Re-ranking
Candidate Generation: The model retrieves 100 products based on user interest.
Attribute Deduplication: The system checks for overlaps in Brand, Category, and Visual Style.
The "Seen/Purchased" Filter: Products with high Jaccard Similarity (is a measure of similarity between two sets) 
to the user’s recent purchase history are suppressed or "down-ranked."
Re-ranking: If the top 5 results are all "running shoes," the system deduplicates the "Category" intent and 
boosts the 6th item (e.g., "running socks") to provide a better user experience.

How to use this for your RAG/Deduplication test:
Duplicate Detection: Look for items sharing the same SKU_Group_ID. These are your "Hard Duplicates."
Near-Duplicate Detection: Use MinHash on the Product_Name. Since I added "Variants" 
(e.g., "Adidas Running Series 10 - Variant Pro"), MinHash should flag these as high-similarity items.
Visual Deduplication: Group by Visual_Embedding_Hash. In real-world RAG, 
you might have two different product descriptions for the same image; this column helps you catch those.
"""


NUM_ITEMS = 200
CATEGORIES = {"Footwear": ["Running"], "Electronics": ["Tech"], "Apparel": ["Casual"], "Audio": ["Travel"], "Kitchen": ["Cooking"]}
BRANDS = {"Footwear": ["Adidas"], "Electronics": ["Apple"], "Apparel": ["Levi's"], "Audio": ["Sony"], "Kitchen": ["Ninja"]}


def generate_long_description(brand, name, category):
    """Generates a ~500 word description with technical specs and marketing fluff."""
    base_text = f"The {brand} {name} represents the pinnacle of {category} engineering. "
    features = [
        "Constructed with premium materials designed for longevity and performance. ",
        "Our proprietary technology ensures that every user experience is seamless and intuitive. ",
        "Ergonomically tested to provide maximum comfort during extended use periods. ",
        "Environmentally conscious manufacturing processes were used to minimize carbon footprint. ",
        "Includes a comprehensive 2-year warranty and 24/7 customer support access. "
    ]
    # Repeat and shuffle to hit the ~500 word mark
    filler = " ".join(features * 15)
    technical_specs = f" SPECIFICATIONS: Weight: {random.randint(100, 900)}g. Dimensions: {random.randint(5, 50)}cm. "
    return (base_text + filler + technical_specs)


def generate_visual_hash():
    return uuid.uuid4().hex[:16]


data = []

for i in range(1, NUM_ITEMS + 1):
    cat = random.choice(list(CATEGORIES.keys()))
    brand = random.choice(BRANDS[cat])
    usage = CATEGORIES[cat][0]

    # Logic for variants (Near-Duplicates)
    if i > 1 and i % 10 == 0:
        prev_item = data[-1]
        name = f"{prev_item['Product_Name']} (Refurbished)"
        sku_group = prev_item['SKU_Group_ID']
        # 98% identical description, just minor changes at the end
        description = prev_item['Product_Description'][:2500] + " [NOTE: This is a certified refurbished unit with minor scuffs.]"
        visual_hash = prev_item['Visual_Embedding_Hash']
    else:
        name = f"{brand} {usage} Model-{random.randint(100, 999)}"
        sku_group = f"SKU-{random.randint(1000, 9999)}"
        description = generate_long_description(brand, name, cat)
        visual_hash = generate_visual_hash()

    data.append({
        "Product_ID": f"P-{i:03d}",
        "Product_Name": name,
        "Brand": brand,
        "Category": cat,
        "SKU_Group_ID": sku_group,
        "Visual_Embedding_Hash": visual_hash,
        "Product_Description": description,
        "Word_Count": len(description.split())
    })

df = pd.DataFrame(data)
df.to_csv("ecommerce_long_desc_dataset.csv", index=False)

# Check a sample
print(f"Generated {len(df)} items.")
print(f"Sample Word Count: {df.iloc[0]['Word_Count']} words.")


# ==========================================================================================
# ==========================================================================================
# ==========================================================================================




# 1. Load the generated dataset
df = pd.read_csv("ecommerce_long_desc_dataset.csv")

# 2. Configuration:
# num_perm: Higher (128-256) increases accuracy for long strings
# threshold: 0.85 to 0.95 is ideal for catching "variants" vs "new products"
lsh = MinHashLSH(threshold=0.9, num_perm=128)


def get_minhash(text):
    """Normalize and create MinHash signature using 7-word shingles."""
    # Normalization (Best Practice for long strings)
    text = re.sub(r'[^\w\s]', '', text.lower())
    words = text.split()

    # 7-word shingles catch semantic phrases rather than just words
    shingles = set([' '.join(words[i:i + 7]) for i in range(len(words) - 6)])

    m = MinHash(num_perm=128)
    for s in shingles:
        m.update(s.encode('utf8'))
    return m


# 3. Process and Identify
unique_ids = []
duplicates_found = 0

print("Starting Deduplication Process...\n")

for idx, row in df.iterrows():
    m = get_minhash(row['Product_Description'])

    # Query if a near-duplicate exists in the LSH index
    result = lsh.query(m)

    if not result:
        lsh.insert(row['Product_ID'], m)
        unique_ids.append(row['Product_ID'])
    else:
        duplicates_found += 1
        print(f"🚩 Found Duplicate: {row['Product_Name']} (ID: {row['Product_ID']})")
        print(f"   Matches existing: {result}\n")

# 4. Results Summary
print("-" * 30)
print(f"Total Items Scanned: {len(df)}")
print(f"Unique Items Kept: {len(unique_ids)}")
print(f"Near-Duplicates Removed: {duplicates_found}")





# import pandas as pd
# import random
# import uuid
# from datetime import datetime, timedelta
#
# # Configuration
# NUM_ITEMS = 200
# CATEGORIES = {
#     "Footwear": ["Running", "Casual", "Hiking", "Formal"],
#     "Electronics": ["Tech", "Office", "Gaming", "Home"],
#     "Apparel": ["Casual", "Sportswear", "Winter", "Sleepwear"],
#     "Audio": ["Travel", "Studio", "Fitness", "Gaming"],
#     "Kitchen": ["Cooking", "Baking", "Coffee", "Appliances"]
# }
# BRANDS = {
#     "Footwear": ["Adidas", "Nike", "On", "Hoka", "New Balance"],
#     "Electronics": ["Apple", "Samsung", "Dell", "HP", "Sony"],
#     "Apparel": ["Levi's", "Patagonia", "Uniqlo", "Zara", "Lululemon"],
#     "Audio": ["Sony", "Bose", "Sennheiser", "JBL", "Beats"],
#     "Kitchen": ["Ninja", "Instant Pot", "KitchenAid", "Breville", "Keurig"]
# }
#
#
# def generate_visual_hash():
#     """Simulates a 16-character perceptual image hash."""
#     return uuid.uuid4().hex[:16]
#
#
# def random_date(start_year=2023):
#     """Generates a random date between start_year and today."""
#     start = datetime(start_year, 1, 1)
#     end = datetime.now()
#     delta = end - start
#     random_days = random.randrange(delta.days)
#     return (start + timedelta(days=random_days)).strftime('%Y-%m-%d')
#
#
# data = []
#
# for i in range(1, NUM_ITEMS + 1):
#     # Select Category and Brand
#     cat = random.choice(list(CATEGORIES.keys()))
#     brand = random.choice(BRANDS[cat])
#     usage = random.choice(CATEGORIES[cat])
#
#     # Create Near-Duplicate Logic
#     # Every 5th item is a "variant" of the previous one to test deduplication
#     if i > 1 and i % 5 == 0:
#         prev_item = data[-1]
#         name = f"{prev_item['Product_Name']} - Variant {random.choice(['XL', 'Pro', 'Elite', 'v2'])}"
#         sku_group = prev_item['SKU_Group_ID']
#         visual_hash = prev_item['Visual_Embedding_Hash']  # Same visual look
#     else:
#         name = f"{brand} {usage} {random.choice(['Series', 'Classic', 'Ultra', 'Max', 'Prime'])} {random.randint(10, 99)}"
#         sku_group = f"SKU-{cat[:3].upper()}-{random.randint(100, 999)}"
#         visual_hash = generate_visual_hash()
#
#     # User History Simulation
#     history = random.choices(["Viewed", "Purchased", "None"], weights=[0.3, 0.1, 0.6])[0]
#
#     data.append({
#         "Product_ID": f"P-{i:03d}",
#         "Product_Name": name,
#         "Brand": brand,
#         "Category": cat,
#         "Usage_Tag": usage,
#         "SKU_Group_ID": sku_group,
#         "Release_Date": random_date(),
#         "Visual_Embedding_Hash": visual_hash,
#         "User_Action_History": history,
#         "Price_USD": round(random.uniform(15.0, 1500.0), 2)
#     })
#
# # Create DataFrame and Save
# df = pd.DataFrame(data)
# df.to_csv("ecommerce_dedup_dataset.csv", index=False)
#
# print(f"Successfully generated {NUM_ITEMS} items.")
# print(df[['Product_Name', 'SKU_Group_ID', 'Visual_Embedding_Hash']].head(10))
