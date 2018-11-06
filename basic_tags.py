import six
import shutil
import os
import stompy.model.delft.waq_scenario as dwaq
six.moves.reload_module(dwaq)

##

hyd_path=('/home/rusty/mirrors/ucd-X/mwtract/TASK2_Modeling/'
          'Hydrodynamic_Model_Files/DELFT3D/Model Run Files/'
          'Feb11_Jun06_2017_08082018-rusty/DFM_DELWAQ_FlowFM/'
          'FlowFM.hyd')
hydro=dwaq.HydroFiles(hyd_path)

class BasicTag(dwaq.Scenario):
    def init_substances(self):
        subs=super(BasicTag,self).init_substances()
        subs['moke']=dwaq.Substance(initial=0.0)
        return subs
    def init_parameters(self):
        params=super(BasicTag,self).init_parameters()
        params['ACTIVE_DYNDEPTH']=1
        params['ACTIVE_TOTDEPTH']=1
        return params

scen=BasicTag(hydro=hydro,name="basic_tag",map_formats=['binary'],
              base_path='runs/basic_tag00')
scen.delft_bin="/home/rusty/src/dfm/1.4.6/bin"
os.environ['LD_LIBRARY_PATH']="/home/rusty/src/dfm/1.4.6/lib"
scen.share_path="/home/rusty/src/dfm/1.4.6/share/delft3d"
# And delft_path must be set to the parent directory of
#  'engines_gpl/waq/default/bloominp.d09'
#  'engines_gpl/waq/default/proc_def'

if os.path.exists(scen.base_path):
    shutil.rmtree(scen.base_path)
scen.cmd_write_hydro()
scen.cmd_write_inp()
scen.cmd_delwaq1()
scen.cmd_delwaq2()
