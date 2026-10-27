import os
import shutil
import urllib.request

ARTIFACT_DIR = r"C:\Users\Riya Vartha\.gemini\antigravity-ide\brain\6c503d5b-f131-4380-8315-175456c5e388"
TARGET_DIR = r"c:\Users\Riya Vartha\Downloads\TARIKA 26\TARIKA\TARIKA-RETAIL\frontend\public\images\products"

# Mapping product IDs to local artifact files or authentic fashion image URLs
PRODUCT_IMAGE_SOURCES = {
    # 1. Pink Ribbed Crop Top
    '8f000001-0000-4000-8000-000000000001': {
        'type': 'local',
        'path': os.path.join(ARTIFACT_DIR, 'ribbed_cotton_top_1793046351688.jpg')
    },
    # 2. White Crew Tee
    '8f000001-0000-4000-8000-000000000002': {
        'type': 'local',
        'path': os.path.join(ARTIFACT_DIR, 'white_crew_tee_1793046405005.jpg')
    },
    # 3. Sage Green Ribbed Knit Top
    '8f000001-0000-4000-8000-000000000003': {
        'type': 'local',
        'path': os.path.join(ARTIFACT_DIR, 'sage_green_top_1793046811824.jpg')
    },
    # 4. Black Square-Neck Fitted Top
    '8f000001-0000-4000-8000-000000000004': {
        'type': 'local',
        'path': os.path.join(ARTIFACT_DIR, 'black_square_top_1793046827769.jpg')
    },
    # 5. Mustard Floral Printed Kurti
    '8f000001-0000-4000-8000-000000000005': {
        'type': 'local',
        'path': os.path.join(ARTIFACT_DIR, 'mustard_floral_kurti_1793046846263.jpg')
    },
    # 6. Powder Blue Embroidered Kurti
    '8f000001-0000-4000-8000-000000000006': {
        'type': 'local',
        'path': os.path.join(ARTIFACT_DIR, 'powder_blue_kurti_1793046860607.jpg')
    },
    # 7. Indigo Handblock Short Peplum Tunic
    '8f000001-0000-4000-8000-000000000007': {
        'type': 'local',
        'path': os.path.join(ARTIFACT_DIR, 'indigo_peplum_tunic_1793046879244.jpg')
    },
    # 8. Beige Tailored Wide-Leg Trousers
    '8f000001-0000-4000-8000-000000000008': {
        'type': 'local',
        'path': os.path.join(ARTIFACT_DIR, 'beige_wide_trousers_1793046893608.jpg')
    },
    # 9. Black Flared Cotton A-Line Skirt
    '8f000001-0000-4000-8000-000000000009': {
        'type': 'local',
        'path': os.path.join(ARTIFACT_DIR, 'black_flared_skirt_1793046909515.jpg')
    },
    # 10. Off-White Flared Rayon Palazzo
    '8f000001-0000-4000-8000-000000000010': {
        'type': 'local',
        'path': os.path.join(ARTIFACT_DIR, 'offwhite_rayon_palazzo_1793046934521.jpg')
    },
    # 11. Olive Green Ankle Tapered Chinos
    '8f000001-0000-4000-8000-000000000011': {
        'type': 'local',
        'path': os.path.join(ARTIFACT_DIR, 'olive_cotton_chinos_1793046952558.jpg')
    },
    # 12. Sky Blue Floral Tiered Sundress
    '8f000001-0000-4000-8000-000000000012': {
        'type': 'local',
        'path': os.path.join(ARTIFACT_DIR, 'sky_blue_sundress_1793046969234.jpg')
    },
    # 13. Terracotta Smocked Fit-and-Flare Dress
    '8f000001-0000-4000-8000-000000000013': {
        'type': 'local',
        'path': os.path.join(ARTIFACT_DIR, 'terracotta_smocked_dress_1793046988676.jpg')
    },
    # 14. Tan Strappy Vegan Leather Flat Sandals
    '8f000001-0000-4000-8000-000000000014': {
        'type': 'url',
        'url': 'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=800&auto=format&fit=crop&q=80'
    },
    # 15. Minimalist White Slip-On Mules
    '8f000001-0000-4000-8000-000000000015': {
        'type': 'url',
        'url': 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800&auto=format&fit=crop&q=80'
    },
    # 16. Embroidered Marigold Mojari Juttis
    '8f000001-0000-4000-8000-000000000016': {
        'type': 'url',
        'url': 'https://images.unsplash.com/photo-1603808033192-082d6919d3e1?w=800&auto=format&fit=crop&q=80'
    },
    # 17. Natural Canvas Mini Shopper Tote
    '8f000001-0000-4000-8000-000000000017': {
        'type': 'url',
        'url': 'https://images.unsplash.com/photo-1544816155-12df9643f363?w=800&auto=format&fit=crop&q=80'
    },
    # 18. Dainty Layered Gold Pendant Necklace
    '8f000001-0000-4000-8000-000000000018': {
        'type': 'url',
        'url': 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800&auto=format&fit=crop&q=80'
    },
    # 19. Traditional Oxidised Silver Jhumkas
    '8f000001-0000-4000-8000-000000000019': {
        'type': 'url',
        'url': 'https://images.unsplash.com/photo-1630019852942-f89202989a59?w=800&auto=format&fit=crop&q=80'
    },
}

def main():
    os.makedirs(TARGET_DIR, exist_ok=True)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for prod_id, src in PRODUCT_IMAGE_SOURCES.items():
        dst_path = os.path.join(TARGET_DIR, f"{prod_id}.jpg")
        if src['type'] == 'local':
            src_file = src['path']
            if os.path.exists(src_file):
                shutil.copyfile(src_file, dst_path)
                size_kb = round(os.path.getsize(dst_path) / 1024, 1)
                print(f"[OK] Copied local image -> {prod_id}.jpg ({size_kb} KB)")
            else:
                print(f"[ERROR] Local source not found: {src_file}")
        elif src['type'] == 'url':
            req = urllib.request.Request(src['url'], headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=15) as resp, open(dst_path, 'wb') as f:
                    f.write(resp.read())
                size_kb = round(os.path.getsize(dst_path) / 1024, 1)
                print(f"[OK] Downloaded URL image -> {prod_id}.jpg ({size_kb} KB)")
            except Exception as e:
                print(f"[ERROR] Failed downloading {src['url']}: {e}")

if __name__ == '__main__':
    main()
