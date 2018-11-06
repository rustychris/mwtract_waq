"""
Brief foray into making waq_scenario more declarative.
A bit more involved than I have the stomach for at the moment.
"""
import six
import shutil
import os
import stompy.model.delft.waq_scenario as dwaq
from stompy.model.delft import dfm_grid

six.moves.reload_module(dfm_grid)
six.moves.reload_module(dwaq)

##
# 'Feb15_Feb20_2017_09172018'
# 'Feb11_Jun06_2017_08082018-rusty'
hyd_path=('/home/rusty/mirrors/ucd-X/mwtract/TASK2_Modeling/'
          'Hydrodynamic_Model_Files/DELFT3D/Model Run Files/'
          'Feb15_Feb20_2017_09172018'
          '/DFM_DELWAQ_FlowFM/FlowFM.hyd')

hydro=dwaq.HydroFiles(hyd_path)

##

scen=dwaq.Scenario()
scen.hydro=hydro
scen.time_step=1000 # 10 minutes
scen.map_time_step=10000 # hourly

##
    def init_substances(self):
        subs=super(AgeTracers,self).init_substances()
        # source tracer:
        subs['moke']=dwaq.Substance(initial=0.0)
        # DWAQ age tracer (exponential decay approach)
        subs['cTr1']=dwaq.Substance(initial=0.0)
        subs['dTr1']=dwaq.Substance(initial=0.0)

        # And integrating age
        subs['NO3']=dwaq.Substance(0)
        subs['ZNit']=dwaq.Substance(0)

        return subs
    def init_parameters(self):
        params=super(AgeTracers,self).init_parameters()
        params['ONLY_ACTIVE']= 1.0
        params['ACTIVE_DYNDEPTH']=1
        params['ACTIVE_TOTDEPTH']=1
        params['ACTIVE_Age1']=1
        params['ACTIVE_Nitrif_NH4']=1
        params['NH4']=10. # inexhaustible
        # disable regular nitrification
        params['RcNit']=0.0
        params['RcNit20']=0.0

        return params

scen=AgeTracers(hydro=hydro,name="age_tracers",map_formats=['binary'],
                base_path='runs/age_02')
scen.delft_bin="/home/rusty/src/dfm/1.4.6/bin"
os.environ['LD_LIBRARY_PATH']="/home/rusty/src/dfm/1.4.6/lib"
scen.share_path="/home/rusty/src/dfm/1.4.6/share/delft3d"
# should make this automatic since it is really useful for interpreting
# output:
scen.map_output = scen.map_output + ('TotalDepth','AgeTr1')

# delwaq2 fails when it goes to the very last timestep
scen.stop_time=scen.hydro.time0 + scen.scu*scen.hydro.t_secs[-2]

# And delft_path must be set to the parent directory of
#  'engines_gpl/waq/default/bloominp.d09'
#  'engines_gpl/waq/default/proc_def'

##

scen.add_bc(boundaries=['MokeBEN'],
            substances=['moke','cTr1','dTr1'],
            data=1.0)

scen.add_bc(boundaries=['MokeBEN'],
            substances=['ZNit'],data=1.0)

##

if os.path.exists(scen.base_path):
    shutil.rmtree(scen.base_path)
scen.cmd_write_hydro()
scen.cmd_write_inp()
scen.cmd_delwaq1()
scen.cmd_delwaq2()
scen.cmd_write_nc()
