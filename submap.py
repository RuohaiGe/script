import open3d as o3d
import numpy as np
import os
import math
import h5py
import time

RADIUS = 10

def create_h5_file(submap, center, file_name):
    f = h5py.File(file_name, 'w')
    f.create_dataset('submap', data=submap)
    f.create_dataset('center', data=center)
    f.close()

    return 0

def load_h5_file(h5_filename):
    f = h5py.File(h5_filename)
    submap = f['submap'][:]
    center = f['center'][:]

    return submap, center

def calc_distance(point_trajectory,point_pointcloud):
    (x_tra,y_tra,z_tra) = (point_trajectory[0], point_trajectory[1], point_trajectory[2])
    (x_pcd,y_pcd,z_pcd) = (point_pointcloud[0], point_pointcloud[1], point_pointcloud[2])
    distance = (x_tra - x_pcd)**2 + (y_tra - y_pcd)**2 + (z_tra - z_pcd)**2
    return math.sqrt(distance) < RADIUS

def create_submap(trajectory_path, pointcloud_path, index):
    dirname = './submap/trajectory' + str(index) + '/'
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    print("Loading pc and creating kd tree")
    start = time.time()
    trajectory_pcd = o3d.io.read_point_cloud(trajectory_path)
    trajectory_pcd_array = np.asarray(trajectory_pcd.points)
    total = len(trajectory_pcd_array)

    pointcloud_pcd = o3d.io.read_point_cloud(pointcloud_path)
    pcd_tree = o3d.geometry.KDTreeFlann(pointcloud_pcd)

    print("finished, elapsed time: {}s".format(time.time()-start))
    count = 0.
    for point_trajectory in trajectory_pcd_array:
        if count % 100 == 0:
            print(count/total*100)
        [k, idx, _] = pcd_tree.search_radius_vector_3d(point_trajectory, RADIUS)

        file_name = 'trajectory' +  '_' + str(index) + '_' + str(count) + '.h5'
        create_h5_file(np.asarray(pointcloud_pcd.points)[idx, :], point_trajectory, dirname+file_name)

        count += 1


def main():
    plyfile = ["./ply/trajectory_1.ply","./ply/pointcloud_1.ply","./ply/trajectory_2.ply","./ply/pointcloud_2.ply","./ply/trajectory_3.ply","./ply/pointcloud_3.ply"
    ,"./ply/trajectory_4.ply","./ply/pointcloud_4.ply","./ply/trajectory_5.ply","./ply/pointcloud_5.ply","./ply/trajectory_6.ply","./ply/pointcloud_6.ply",
    "./ply/trajectory_7.ply","./ply/pointcloud_7.ply","./ply/trajectory_8.ply","./ply/pointcloud_8.ply","./ply/trajectory_9.ply","./ply/pointcloud_9.ply"]
    for index in range(9,10):
        print(plyfile[(index-1)*2],plyfile[(index-1)*2+1])
        create_submap(plyfile[(index-1)*2],plyfile[(index-1)*2+1],index)

main()
