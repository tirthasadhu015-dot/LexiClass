
import pandas as pd

annotation_file = "dataset/annotations/annotation_template.csv"
parquet_file = "dataset/raw/train-00000 (1).parquet"

annotations = pd.read_csv(annotation_file)
data = pd.read_parquet(parquet_file)

missing = annotations[annotations["annotation_notes"].isna()]

for _, item in missing.iterrows():
    doc_id = item["document_id"]

    document = data[data["doc_id"] == doc_id]

    print("\n" + "=" * 80)
    print("TITLE:", item["document_title"])
    print("CURRENT CATEGORY:", item["category"])
    print("=" * 80)

    if not document.empty:
        print(document.iloc[0]["text"][:12000])
    else:
        print("Document not found in Parquet.")
