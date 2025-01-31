import grid
import pyvis_test
import argparse










def main():
    parser = argparse.ArgumentParser(description ='Create a Grid World')
    parser.add_argument('--x_size', type=int , default=10,  required=False ,help='The size of the grid in the X direction' )
    parser.add_argument('--y_size', type=int , default=10,  required=False ,help='The size of the grid in the Y direction' )
    parser.add_argument('--coverage', type=float , default=0.1,  required=False ,help='What percent of the grid will be covered with obstacles' )
    parser.add_argument('--square_size', type=int , default=1,  required=False ,help='How large each square in an obstacle will be' )
    
    args = parser.parse_args()
    graph_generator = grid.generate_graph(args.x_size, args.y_size, args.coverage, args.square_size)
    map,shapes = graph_generator.make_grid()
    print(shapes)
    net = pyvis_test.create_polygon_network(shapes, args.x_size)
    net.show("my_polygons.html")
    # pass

if __name__ == "__main__":
    main()