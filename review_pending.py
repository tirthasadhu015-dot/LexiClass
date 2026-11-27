
import pandas as pd

annotation_file = "dataset/annotations/annotation_template.csv"
parquet_file = "dataset/raw/train-00000 (1).parquet"

annotations = pd.read_csv(annotation_file)
data = pd.read_parquet(parquet_file)

pending = annotations[
    annotations["reviewer_status"] == "REVIEW_REQUIRED"
]

for _, item in pending.iterrows():
    doc_id = item["document_id"]
    document = data[data["doc_id"] == doc_id]

    print("\n" + "=" * 90)
    print("TITLE:", item["document_title"])
    print("DOCUMENT ID:", doc_id)
    print("=" * 90)

    if not document.empty:
        print(str(document.iloc[0]["text"])[:12000])
    else:
        print("Document not found in Parquet.")
