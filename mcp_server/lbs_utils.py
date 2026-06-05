from geopy.distance import geodesic

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    計算兩個座標之間的直線距離 (單位：公尺)
    """
    coord1 = (lat1, lon1)
    coord2 = (lat2, lon2)
    
    # geodesic 回傳的是距離物件，我們將其轉為公尺
    return geodesic(coord1, coord2).meters