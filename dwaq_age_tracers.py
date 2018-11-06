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

class AgeTracers(dwaq.Scenario):
    # not required, but dwaq allows 3 lines of descriptive
    # text for the run.
    desc=('Age tracers',
          'testing multiple tracer approaches',
          'v00')
    # time steps are in HHMMSS, so 1000 is 10 minutes
    # 1 hour unstable, 10 minutes okay.
    time_step=1000
    # map output hourly - and 10000 is 1 hour
    map_time_step=10000

    def init_substances(self):
        # allocate the substance dictionary
        subs=super(AgeTracers,self).init_substances()

        # then add tracers for this run
        # source tracers -- default to an initial condition of 0
        # these will be associated with specific boundary locations
        # later
        subs['moke']=dwaq.Substance()
        subs['sac'] =dwaq.Substance()
        subs['mokesj']=dwaq.Substance()
        subs['lps'] =dwaq.Substance()
        subs['snodlambert']=dwaq.Substance()
        subs['middle']=dwaq.Substance()
        subs['lost']=dwaq.Substance()

        subs['ic']  =dwaq.Substance(initial=1.0)

        # DWAQ age tracer (exponential decay approach).  DWAQ
        # has a built-in process for this
        subs['cTr1']=dwaq.Substance()
        subs['dTr1']=dwaq.Substance()

        # And integrating age -- this requires "repurposing" some
        # nutrient processes
        # The simplest approach would use NO3 and ZNit, a zeroth order
        # process creating NO3.
        #subs['NO3']=dwaq.Substance(0)
        #subs['ZNit']=dwaq.Substance(0)
        # To allow for partial age approaches, track RcNit
        # and optionally specify a variable NH4.
        # TODO: this is currently aging at 0.7 the nominal rate.
        #  SWVnNit defaults to 0, "pragmatic" kinetics
        # 
        subs['NO3']=dwaq.Substance(0)
        subs['RcNit']=dwaq.Substance(0)
        # RcNit20=0.0

        return subs

    def init_bcs(self):
        super(AgeTracers,self).init_bcs()
        # FlowFM.bnd lists the names available for boundaries

        # For the decay tracers, cTr1 and dTr1 have to get the
        # same value.
        # For CART tracer, RcNit gets 1.0
        self.add_bc(boundaries=['MokeBEN'],
                    substances=['moke','cTr1','dTr1','RcNit'],
                    data=1.0)
        self.add_bc(boundaries=['LostBEN'],
                    substances=['lost'],
                    data=1.0)
        self.add_bc(boundaries=['SacDCC'],
                    substances=['sac'],
                    data=1.0)
        self.add_bc(boundaries=['MokeSJ'],
                    substances=['mokesj'],
                    data=1.0)
        self.add_bc(boundaries=['LPS'],
                    substances=['lps'],
                    data=1.0)
        self.add_bc(boundaries=['SnodLambert'],
                    substances=['snodlambert'],
                    data=1.0)
        self.add_bc(boundaries=['MiddleBEN'],
                    substances=['middle'],
                    data=1.0)

    def init_parameters(self):
        params=super(AgeTracers,self).init_parameters()
        params['ONLY_ACTIVE']= 1.0
        params['ACTIVE_DYNDEPTH']=1
        params['ACTIVE_TOTDEPTH']=1
        # TotalDepth output is needed to post-process the output
        self.map_output = self.map_output + ('TotalDepth',)

        params['ACTIVE_Age1']=1
        # the calculated age value must be requested in the output
        self.map_output = self.map_output + ('AgeTr1',)

        params['ACTIVE_Nitrif_NH4']=1
        params['NH4']=1. # inexhaustible
        params['TcNit']=1. # no temperature variation
        # for the zeroth order approach we'd disable regular nitrification
        # params['RcNit']=0.0

        return params

scen=AgeTracers(hydro=hydro,
                name="age_tracers",
                map_formats=['binary'],
                base_path='runs/age_03')

# Configure where to find DWAQ
scen.delft_bin="/home/rusty/src/dfm/1.4.6/bin"
os.environ['LD_LIBRARY_PATH']="/home/rusty/src/dfm/1.4.6/lib"
scen.share_path="/home/rusty/src/dfm/1.4.6/share/delft3d"
# And delft_path must be set to the parent directory of
#  'engines_gpl/waq/default/bloominp.d09'
#  'engines_gpl/waq/default/proc_def'

# delwaq2 fails when it goes to the very last timestep of DFM output
scen.stop_time=scen.hydro.time0 + scen.scu*scen.hydro.t_secs[-2]

##

if os.path.exists(scen.base_path):
    shutil.rmtree(scen.base_path)

scen.cmd_write_hydro()
scen.cmd_write_inp()
scen.cmd_delwaq1()
scen.cmd_delwaq2()
scen.cmd_write_nc()
