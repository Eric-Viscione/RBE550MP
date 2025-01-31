from pyvis.network import Network
import numpy as np

def create_polygon_network(polygons, size, title="Polygon Network"):
    """
    Create an interactive network visualization of polygons.
    
    Args:
        polygons: List of lists containing (x,y) coordinates for each polygon
        title: Title for the network visualization
    """
    # Initialize network
    net = Network(height=f"{size*size}px", width="100%", bgcolor="#ffffff", notebook=True)
    net.toggle_physics(False)  # Disable physics simulation for static polygon display
    
    # Keep track of node IDs
    node_id = 0
    print(f"Shapes data: {polygons}")  
    print(f"Type of shapes: {type(polygons)}")  
    for poly_idx, polygon in enumerate(polygons):
        print(f"Shapes data: {polygon}")  
        print(f"Type of shapes: {type(polygon)}")  
        # Create nodes for each corner
        corner_ids = []
        for x, y in polygon:
            net.add_node(
                node_id,
                label=f"({x}, {y})",
                x=x * 1,  # Scale coordinates for better visualization
                y=y * 1,
                color=f"#{poly_idx*30:02x}{'80':s}{'80':s}",  # Different color for each polygon
                size=1
            )
            corner_ids.append(node_id)
            node_id += 1
        
        # Create edges between corners
        for i in range(len(corner_ids)):
            net.add_edge(
                corner_ids[i],
                corner_ids[(i + 1) % len(corner_ids)],
                color=f"#{poly_idx*30:02x}{'80':s}{'80':s}"
            )
    
    return net


# Add custom options for more control
def create_custom_polygon_network(
    polygons,
    node_colors=None,
    edge_colors=None,
    node_sizes=None,
    edge_widths=None,
    labels=None
):
    """
    Create a more customizable polygon network visualization.
    
    Args:
        polygons: List of lists containing (x,y) coordinates
        node_colors: List of colors for nodes
        edge_colors: List of colors for edges
        node_sizes: List of node sizes
        edge_widths: List of edge widths
        labels: List of custom labels for nodes
    """
    net = Network(height="750px", width="100%", bgcolor="#ffffff", notebook=True)
    net.toggle_physics(False)
    
    node_id = 0
    for poly_idx, polygon in enumerate(polygons):
        corner_ids = []
        for i, (x, y) in enumerate(polygon):
            node_color = node_colors[node_id] if node_colors else f"#{poly_idx*30:02x}{'80':s}{'80':s}"
            node_size = node_sizes[node_id] if node_sizes else 20
            label = labels[node_id] if labels else f"({x}, {y})"
            
            net.add_node(
                node_id,
                label=label,
                x=x * 100,
                y=y * 100,
                color=node_color,
                size=node_size
            )
            corner_ids.append(node_id)
            node_id += 1
        
        # Create edges
        for i in range(len(corner_ids)):
            edge_idx = poly_idx * len(polygon) + i
            edge_color = edge_colors[edge_idx] if edge_colors else f"#{poly_idx*30:02x}{'80':s}{'80':s}"
            edge_width = edge_widths[edge_idx] if edge_widths else 1
            
            net.add_edge(
                corner_ids[i],
                corner_ids[(i + 1) % len(corner_ids)],
                color=edge_color,
                width=edge_width
            )
    

