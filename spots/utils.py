import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    2点の緯度経度から距離（メートル）を計算する関数（ヒュベニの公式の簡易版）
    """
    R = 6371000  # 地球の半径 (メートル)
    
    # ラジアンに変換
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c