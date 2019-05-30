
# - Denavit-Hartemberg method.
# This script receive all required parameters to compute the direct kinematics of the MS. Here each transformation
# matrix is computed and then used to get the coordinates of the end effector.

from numpy import zeros, array, deg2rad, delete, cos, sin

def TM(th, cA, sA, A, D, cB, sB):  # Compute each transformation matrix with the parameters Theta, Alpha, A & D
    
    Tmx = zeros((len(th),4,4))
    
    for i in range(0,len(th)):
        
        t = th[i]
        cAi = cA[i]
        sAi = sA[i]
        Ai = A[i]
        Di = D[i]
        cBi = cB
        sBi = sB
        
        if i != 2:
            
            Tmx[i] = array([[cos(t), -sin(t), 0, Ai],
                          [sin(t)*cAi, cos(t)*cAi, -sAi, -Di*sAi],
                          [sin(t)*sAi, cos(t)*sAi, cAi, cAi*Di],
                          [0, 0, 0, 1]])
            
        if i == 2:
            Tmx[i] = array([[cos(t)*cBi, -sin(t)*cBi, sBi, (sBi*Di+Ai)],
                           [(sin(t)*cAi+sAi*sBi*cos(t)), (cos(t)*cAi-sAi*sBi*sin(t)), -sAi*cBi, -Di*sAi*cBi],
                           [(sin(t)*sAi-cAi*sBi*cos(t)), (cos(t)*sAi+sin(t)*sBi*cAi), cAi*cBi, cBi*cAi*Di],
                           [0, 0, 0, 1]])
    return Tmx

def DH(T, cA, sA, A, D, cB, sB):  # Theta, Alpha, A y D parameters for DH form & Betha
    
    T = deg2rad(T)
    
    Tm = zeros((len(T),4,4))  # Set the initial result matrix.
    
    Tm = TM(T, cA, sA, A, D, cB, sB)
     
    M = Tm[0]@Tm[1]@Tm[2]@Tm[3]@Tm[4]@Tm[5]  # Get the final transformation matrix.
    M = delete(M,3,0) # Delete the four row of zeros and ones
    coordinates = M[:,3]

    return M, coordinates