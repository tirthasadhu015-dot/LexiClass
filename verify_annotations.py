
import pandas as pd

file = "dataset/annotations/annotation_template.csv"
df = pd.read_csv(file)

print("\nTOTAL DOCUMENTS:", len(df))

print("\nCATEGORY COUNTS:")
print(df["category"].value_counts().to_string())

print("\nREVIEW STATUS:")
print(df["reviewer_status"].value_counts().to_string())

print("\nMISSING ANNOTATION NOTES:")
print(df["annotation_notes"].isna().sum())

print("\nREVIEW REQUIRED DOCUMENTS:")
print(
    df[df["reviewer_status"] == "REVIEW_REQUIRED"][
        ["document_title", "category"]
    ].to_string(index=False)
)

print("\nVERIFICATION COMPLETED")
