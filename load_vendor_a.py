from src.embed import add_documents

add_documents(filepath='data/vendors/vendor_a/contract.txt', source_label='vendor_a_contract', collection_name='vendor_a')
add_documents(filepath='data/vendors/vendor_a/privacy_policy.txt', source_label='vendor_a_privacy_policy', collection_name='vendor_a')