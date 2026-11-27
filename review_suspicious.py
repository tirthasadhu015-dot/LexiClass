
import pandas as pd

parquet_file = "dataset/raw/train-00000 (1).parquet"

data = pd.read_parquet(parquet_file)

keywords = [
    "Goa Agricultural Produce and Livestock Marketing",
    "ODISHA SHOPS AND COMMERCIAL ESTABLISHMENTS",
    "Uttar Pradesh Education Service Selection Commission",
    "Uttar Pradesh Sugarcane Cess"
]

for keyword in keywords:
    matches = data[
        data["document_title"].str.contains(
            keyword, case=False, na=False
        )
    ]

    for _, doc in matches.iterrows():
        print("\n" + "=" * 90)
        print("DOCUMENT ID:", doc["doc_id"])
        print("TITLE:", doc["document_title"])
        print("=" * 90)
        print(str(doc["text"])[:10000])
        print("\n")
