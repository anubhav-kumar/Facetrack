import boto3

client=boto3.client('rekognition')
response=client.list_collections(MaxResults=100)
collection_ids=response['CollectionIds']

for collection_id in collection_ids:
    print("Deleting collection: " + collection_id)
    client.delete_collection(CollectionId=collection_id)
    print("Deleted collection: " + collection_id)

