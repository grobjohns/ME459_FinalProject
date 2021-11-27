from numpy.lib.function_base import disp
from Bodies import *
import numpy as np

# All equations are copied/derived from
# https://enterfea.com/finite-element-analysis-by-hand/

def print_forces(forces):
    i = 0
    for force in forces:
        print("F_" + str(i+1) + ": " + str(round(forces[i],5)) + "N")
        i += 1

def print_displacements(displacements,global_displacement=None):
    i = 0
    for displacement in displacements:
        print("ΔL_" + str(i+1) + ": " + str(round((10**3)*displacements[i],5)) + "mm")
        i += 1
    if global_displacement is not None:
        print("ΔL_global: " + str(round((10**3)*global_displacement,5)) + "mm")

# This is from the first simple example
# Solves setup given EITHER force (N) or displacement (m)
# Force and displacement are both numpy column vectors
def Solve_SimpleAxialTension(workpiece,force=None,displacement=None):
    coeff = (workpiece.area * workpiece.modulus) / workpiece.length # AE / L
    stiffness = (np.eye(2) * 2) - 1.0
    stiffness *= coeff

    if displacement != None and force == None: # displacement is given, solve for force
        displacement_col = np.array([0,displacement]).T # left side (ΔL_1) is pinned
        force_col = np.matmul(stiffness,displacement_col) # B = Ax

    if force != None and displacement == None: # force is given, solve for displacement
        force_col = np.array([-force,force]).T # equal and opposite reaction force
        # stiffness is a singular matrix, so the method of least squares is needed to solve
        displacement_col = np.linalg.lstsq(stiffness,force_col)[0] 
        total_displacement = abs(displacement_col[0])+abs(displacement_col[1])
        displacement_col = np.array([0,total_displacement]).T # left side (ΔL_1) is pinned

    if force == None and displacement == None:
        print("No force/displacement given")
        return

    print_forces(force_col)
    print_displacements(displacement_col)

# Allows you to solve for local/global displacement, given pairs of locations and forces.
# The area is assumed to be the same along the entire piece.
# force_pos_pairs is an array of (node,force) tuples. Positive force = tension.
def Solve_MultipleAxialTension(workpiece,pos_force_pairs,nodes):
    node_length = workpiece.length / (nodes*(.5*(nodes-1))) # why does this line work? couldn't tell you.
    coeff = (workpiece.area * workpiece.modulus) / node_length
    local_stiffness = (np.eye(2) * 2) - 1.0
    local_stiffness *= coeff
    global_stiffness = np.zeros([nodes,nodes])
    for i in range(nodes-1):
        global_stiffness[i:i+2,i:i+2] += local_stiffness
    forces = np.zeros([nodes,1])
    for pair in pos_force_pairs:
        pos, force = pair
        forces[pos-1] += force
    forces[0] = -sum(forces)
    displacements = np.linalg.lstsq(global_stiffness,forces)[0]
    offset = 0
    for i in range(nodes-1):
        if displacements[i] < 0:
            offset -= displacements[i]
    #offset = displacements[0]
    #displacements += offset
    displacements -= displacements[0]
    print_forces(forces.T[0])
    print_displacements(displacements.T[0],global_displacement=sum(displacements.T[0]))
    



## Function tests
#  Results can be verified with
#  https://www.omnicalculator.com/physics/stress
piece = SquarePrism(Elasticity.ALUMINUM.value,.1,5.0)
#Solve_SimpleAxialTension(piece)
#Solve_SimpleAxialTension(piece,displacement=.01)
Solve_SimpleAxialTension(piece,force=50000)
Solve_MultipleAxialTension(piece,[(10,50000)],10)