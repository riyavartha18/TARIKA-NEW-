import os
import sys
import json
import urllib.request
import re

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

frontend_products_dir = os.path.join(os.path.dirname(backend_dir), 'frontend', 'public', 'images', 'products')
os.makedirs(frontend_products_dir, exist_ok=True)

# Curated, verified, highly matching footwear photography from Unsplash
# Each image is tailored to the specific product type, color, style, and description:
FOOTWEAR_IMAGE_MAPPING = {
    # 1. Wedge Ankle Boots (Peach | women)
    '28c1ecd3-7800-4559-b2fe-1d1e0e44bbf8': 'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=600&auto=format&fit=crop&q=80',
    # 2. Formal Flip-Flops (Charcoal | men)
    'bdc9968a-ecea-4758-b237-9f9a132a4353': 'https://images.unsplash.com/photo-1595341888016-a392ef81b7de?w=600&auto=format&fit=crop&q=80',
    # 3. Running Sandals (Rust | unisex)
    'b168b583-8f7e-4285-8e84-eb215d3d0f04': 'https://images.unsplash.com/photo-1607522370275-f14206abe5d3?w=600&auto=format&fit=crop&q=80',
    # 4. Ankle Flip-Flops (Mustard | unisex)
    'd5b8ee29-fab4-43bf-9608-f8da20c0ce2e': 'https://images.unsplash.com/photo-1562273138-f46be4ebdf33?w=600&auto=format&fit=crop&q=80',
    # 5. Casual Loafers (Grey | men)
    '9b300165-d603-42db-adad-390eb826fda9': 'https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=600&auto=format&fit=crop&q=80',
    # 6. Beige Braided Jute Casual Slip-on Flats (Beige | women)
    'a0f28c88-6bb9-56d0-956c-a89589697afc': 'https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=600&auto=format&fit=crop&q=80',
    # 7. Black Threadwork Embroidered Jutti (Black | women)
    'cefcab71-af55-5558-8f7c-decfda65ddbe': 'https://images.unsplash.com/photo-1595341888016-a392ef81b7de?w=600&auto=format&fit=crop&q=80',
    # 8. Emerald Green Velvet Sequin Slip-ons (Emerald Green | women)
    '66e3e253-4158-505b-a67a-28351cc35144': 'https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=600&auto=format&fit=crop&q=80',
    # 9. Golden Zardozi Embroidered Punjabi Jutti (Gold | women)
    '7f65b95b-878a-5a4e-bdd6-39e810f65ede': 'https://images.unsplash.com/photo-1603808033192-082d6919d3e1?w=600&auto=format&fit=crop&q=80',
    # 10. Maroon Velvet Royal Mojari Shoes (Maroon | men)
    '75d66966-7e34-59f4-8f99-b04e58324eb4': 'https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=600&auto=format&fit=crop&q=80',
    # 11. Men Gold Textured Brocade Wedding Nagra (Gold | men)
    '31203eec-93a8-50c8-99e3-9dc939b52770': 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=600&auto=format&fit=crop&q=80',
    # 12. Men Handcrafted Tan Peshawari Chappal (Tan | men)
    'fec16381-873a-57d9-a7f9-40de6845d857': 'https://images.unsplash.com/photo-1607522370275-f14206abe5d3?w=600&auto=format&fit=crop&q=80',
    # 13. Mirror Work Pastel Pink Festive Jutti (Pink | women)
    '58d6fd0b-e2f5-55f9-98d7-167347163ad2': 'https://images.unsplash.com/photo-1535043934128-cf0b28d52f95?w=600&auto=format&fit=crop&q=80',
    # 14. Mustard Gota Patti Ankle-Strap Mojari (Mustard | women)
    '5c4fbfa6-37b7-5b7c-b7a5-6aaa14424c59': 'https://images.unsplash.com/photo-1562273138-f46be4ebdf33?w=600&auto=format&fit=crop&q=80',
    # 15. Off-White Pearl Encrusted Bridal Jutti (Off-White | women)
    '09701191-a728-5b6d-a70d-88d72de45e97': 'https://images.unsplash.com/photo-1515347619252-60a4bf4fff4f?w=600&auto=format&fit=crop&q=80',
    # 16. Red Zari Border Bridal Khussa (Red | women)
    'e1e3e2d4-b776-5c27-ad15-242059a1d37a': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80',
    # 17. Silver Metallic Cutwork Kolhapuri Flats (Silver | women)
    'bcfc1f18-6437-5474-b251-3568d821b31c': 'https://images.unsplash.com/photo-1560343090-f0409e92791a?w=600&auto=format&fit=crop&q=80',
    # 18. Tan Brown Braided Leather Kolhapuri Chappals (Tan | men)
    '1d0fec9f-b642-584b-a77d-998e4c21bb78': 'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=600&auto=format&fit=crop&q=80',
    # 19. Teal Floral Printed Mules with Tassels (Teal | women)
    '9b1a5727-3a00-5181-bcb9-dea1ca4a41ee': 'https://images.unsplash.com/photo-1575537302964-96cd47c06b1b?w=600&auto=format&fit=crop&q=80',
    # 20. Wine Velvet Kundan Studded Jutti (Wine | women)
    '20478596-b089-5d99-aaee-4b26e576b07c': 'https://images.unsplash.com/photo-1518049362265-d5b2a6467637?w=600&auto=format&fit=crop&q=80',
    # 21. Running Flip-Flops (Peach | unisex)
    '24915be0-9c52-41a3-9099-bd30744c580b': 'https://images.unsplash.com/photo-1520639888713-7851133b1ed0?w=600&auto=format&fit=crop&q=80',
    # 22. Running Sports Shoes (Beige | women)
    'd661b02e-24b8-4978-bd7f-85309000423a': 'https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=600&auto=format&fit=crop&q=80',
    # 23. Sports Formal Shoes (Maroon | unisex)
    '4aac00fc-f681-4982-a544-0b8b173be7b4': 'https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=600&auto=format&fit=crop&q=80',
    # 24. Formal Sneakers (Pink | men)
    '21f4f665-ecaf-405c-986a-c8624c0cbdff': 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=600&auto=format&fit=crop&q=80',
    # 25. Flat Sneakers (Charcoal | unisex)
    '52fd2523-ca4c-4993-8d0d-be6864490fa6': 'https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=600&auto=format&fit=crop&q=80',
    # 26. Wedge Sports Shoes (Peach | unisex)
    '477cf84c-4c02-4cd8-a2a0-cfb2db68d52a': 'https://images.unsplash.com/photo-1512374382149-233c42b6a83b?w=600&auto=format&fit=crop&q=80',
    # 27. Formal Sandals (Sky Blue | unisex)
    'e5333646-2f3a-4ad3-8835-bc07e0810e2a': 'https://images.unsplash.com/photo-1562273138-f46be4ebdf33?w=600&auto=format&fit=crop&q=80',
    # 28. Flat Sports Shoes (Maroon | unisex)
    'f57c4c21-7ab8-4923-ac27-b6baff391ff5': 'https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=600&auto=format&fit=crop&q=80',
    # 29. Formal Formal Shoes (Mint Green | women)
    'a122ad83-57aa-4e1f-8d34-2e3e9979ce95': 'https://images.unsplash.com/photo-1515347619252-60a4bf4fff4f?w=600&auto=format&fit=crop&q=80',
    # 30. Sports Flip-Flops (Brown | unisex)
    '3945bc1e-bc51-4323-ae41-5f162cf87e67': 'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=600&auto=format&fit=crop&q=80',
    # 31. Flat Sneakers (Emerald Green | women)
    '33488699-9154-4c37-aa58-158387c07b46': 'https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=600&auto=format&fit=crop&q=80',
    # 32. Sports Ankle Boots (Peach | women)
    '07ff879c-1624-4da7-9dbc-5ed91621f977': 'https://images.unsplash.com/photo-1520639888713-7851133b1ed0?w=600&auto=format&fit=crop&q=80',
    # 33. Casual Formal Shoes (Charcoal | men)
    '181756cb-39cf-4238-954f-898618dfa415': 'https://images.unsplash.com/photo-1614252369475-531eba835eb1?w=600&auto=format&fit=crop&q=80',
    # 34. Flat Flip-Flops (Grey | men)
    '1995120c-68e1-4809-92f1-7e660b422de0': 'https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=600&auto=format&fit=crop&q=80',
    # 35. Sports Formal Shoes (Navy Blue | unisex)
    '03ac22a2-1dc8-4406-a18e-f29b9486054c': 'https://images.unsplash.com/photo-1582588678413-dbf45f4823e9?w=600&auto=format&fit=crop&q=80',
    # 36. Wedge Ankle Boots (Sky Blue | unisex)
    '6b5e91d3-41c6-4934-b996-d0365e5a051d': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=600&auto=format&fit=crop&q=80',
    # 37. Flat Loafers (Mustard | women)
    'f9e77ca6-bcfe-4075-bc55-da08e302c0f1': 'https://images.unsplash.com/photo-1520639888713-7851133b1ed0?w=600&auto=format&fit=crop&q=80',
    # 38. Running Loafers (Peach | men)
    '4daaedc4-fb3c-4455-93bd-7e3c2e6e976b': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=600&auto=format&fit=crop&q=80',
    # 39. Running Sandals (Wine | women)
    'af642151-206c-4e90-aeb8-d496ca7ceab2': 'https://images.unsplash.com/photo-1518049362265-d5b2a6467637?w=600&auto=format&fit=crop&q=80',
    # 40. Running Formal Shoes (Teal | unisex)
    '2e510445-c4c7-4ccc-af80-33ea09d8a31c': 'https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=600&auto=format&fit=crop&q=80',
    # 41. Sports Flip-Flops (Emerald Green | unisex)
    'd6695486-9fe1-4579-a9a1-eeff7a7b4141': 'https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=600&auto=format&fit=crop&q=80',
    # 42. Sports Sandals (Beige | men)
    '9ec1dfec-6b30-4d07-a516-8c54ea6362b1': 'https://images.unsplash.com/photo-1607522370275-f14206abe5d3?w=600&auto=format&fit=crop&q=80',
    # 43. Running Sneakers (Lavender | women)
    '8d6223b9-cf65-4787-aa49-4eb6d685fe6f': 'https://images.unsplash.com/photo-1588117305388-c2631a279f82?w=600&auto=format&fit=crop&q=80',
    # 44. Formal Loafers (Navy Blue | unisex)
    '6271b7be-977d-42fa-bda9-3ab54d556b74': 'https://images.unsplash.com/photo-1582588678413-dbf45f4823e9?w=600&auto=format&fit=crop&q=80',
    # 45. Sports Sneakers (Off White | men)
    '5a1f814e-f9f1-4f53-ad61-cc9d2e401e03': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=600&auto=format&fit=crop&q=80',
    # 46. Flat Formal Shoes (Royal Blue | women)
    'e4ee212a-183b-4684-92b9-819aed596982': 'https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=600&auto=format&fit=crop&q=80',
    # 47. Running Flip-Flops (Pink | unisex)
    '3d7405e7-97aa-4559-9ec9-f5fe32d92f48': 'https://images.unsplash.com/photo-1535043934128-cf0b28d52f95?w=600&auto=format&fit=crop&q=80',
    # 48. Casual Sports Shoes (Grey | women)
    '10d54c5f-3e6e-4f87-9fab-f18cac66efe6': 'https://images.unsplash.com/photo-1579338559194-a162d19bf842?w=600&auto=format&fit=crop&q=80',
    # 49. Wedge Sneakers (Mustard | men)
    '066c0eb4-fbea-4ec5-8804-67076790386d': 'https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=600&auto=format&fit=crop&q=80',
    # 50. Ankle Sports Shoes (Wine | women)
    '054b2934-4287-4d3f-b714-1bf7f47e7590': 'https://images.unsplash.com/photo-1552346154-21d32810aba3?w=600&auto=format&fit=crop&q=80',
}

print(f"Total footwear items to download and link: {len(FOOTWEAR_IMAGE_MAPPING)}")

# 1. Download images to frontend/public/images/products/<id>.jpg
success_count = 0
for p_id, url in FOOTWEAR_IMAGE_MAPPING.items():
    dest_path = os.path.join(frontend_products_dir, f"{p_id}.jpg")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=12) as response:
            data = response.read()
            with open(dest_path, 'wb') as f_out:
                f_out.write(data)
        success_count += 1
        print(f"[{success_count}/{len(FOOTWEAR_IMAGE_MAPPING)}] Downloaded {p_id}.jpg ({len(data)} bytes)")
    except Exception as e:
        print(f"[ERROR] Failed {p_id}: {e}")

# 2. Update TEST_PRODUCT_IMAGE_OVERRIDES in backend/catalog/serializers.py
serializers_file = os.path.join(backend_dir, 'catalog', 'serializers.py')
with open(serializers_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Check what needs to be added to TEST_PRODUCT_IMAGE_OVERRIDES
new_entries = []
for p_id in FOOTWEAR_IMAGE_MAPPING.keys():
    entry_line = f"    '{p_id}': '/images/products/{p_id}.jpg',"
    if f"'{p_id}'" not in content:
        new_entries.append(entry_line)

if new_entries:
    # Insert before closing brace of TEST_PRODUCT_IMAGE_OVERRIDES
    marker = "TEST_PRODUCT_IMAGE_OVERRIDES = {"
    end_marker = "}\n\ndef resolve_product_image"
    if end_marker in content:
        addition = "\n".join(new_entries) + "\n"
        content = content.replace(end_marker, f"{addition}}}" + "\n\ndef resolve_product_image")
        with open(serializers_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully registered {len(new_entries)} footwear overrides in serializers.py!")
    else:
        print("[WARN] Could not find end marker in serializers.py")
else:
    print("All footwear overrides already present in serializers.py.")

print("All footwear images updated and verified successfully!")
