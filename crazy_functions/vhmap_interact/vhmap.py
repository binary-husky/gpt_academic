from toolbox import update_ui, get_conf, trimmed_format_exc
import threading

def Singleton(cls):
    _instance = {}
 
    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]
 
    return _singleton

@Singleton
class vhmp_interface():
    def __init__(self) -> None:
        from VISUALIZE.mcom_rt import mcom
        self.vis3d = mcom(path='TEMP/v2d_logger/', draw_mode='Threejs')
        self.vis3d.v2d_init()
        self.vis3d.设置样式('star')
        # vis3d.设置样式('star')       # 布置星空
        self.vis3d.其他几何体之旋转缩放和平移('box', 'BoxGeometry(1,1,1)',   0,0,0,  1,1,1, 0,0,0) 
        # declare geo 'oct1', init with OctahedronGeometry, then (1)rotate & (2)scale & (3)translate
        self.vis3d.其他几何体之旋转缩放和平移('octahedron', 'OctahedronGeometry(1,0)', 0,0,0,  1,1,1, 0,0,0)   # 八面体
        # 需要换成其他几何体，请把'OctahedronGeometry(1,0)'替换，参考网址 https://threejs.org/docs/index.html?q=Geometry
        self.vis3d.其他几何体之旋转缩放和平移('sphere', 'SphereGeometry(1)',   0,0,0,  1,1,1, 0,0,0) # 球体
        self.vis3d.其他几何体之旋转缩放和平移('cylinder', 'CylinderGeometry(1,1,5,32)',   0,0,0,  1,1,1, 0,0,0) # 球体

    def update(self, json):
        for obj in json:
            self.vis3d.发送几何体(
                f'{obj["geometry"]}|{obj["name"]}|{obj["color"]}|{obj["size"]}',   # 填入 ‘形状|几何体之ID标识|颜色|大小’即可
                obj["location_x"], 
                obj["location_y"], 
                obj["location_z"],
                ro_x=0, ro_y=0, ro_z=0,                         # 三维位置+欧拉旋转变换，六自由度
                track_n_frame=0)                                # 显示历史20帧留下的轨迹
        self.vis3d.结束关键帧()
