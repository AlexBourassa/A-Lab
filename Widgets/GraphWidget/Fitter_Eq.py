# -*- coding: utf-8 -*-
"""
@author: AlexBourassaandre Bourassa

@TODO:  Auto Generate the fitFct dict
"""

import numpy as _np

from scipy.optimize import leastsq

#import inspect as _inspect
#all_functions = _inspect.getmembers()
#fitFct = dict()
#listing =  dir()
#print listing
#for class_name in listing:
#    print class_name
#    print eval(class_name)
#    try: 
#        class_inst = eval(class_name)
#        if Generic_Fct in class_inst.__bases__: 
#            print class_name
#            fitFct[class_name] = class_inst()
#    except: pass
#!!!  Edit this when adding or removing functions  !!!
def getAllFitFct():
    """
    Returns a dictionary associting each fit fct with an instance of it's class
    """
    fitFct = {'Laurentzian':Laurentzian(), 'Gaussian':Gaussian(), 'Cos':Cos(), 'LaurentzianWithConstInterference':LaurentzianWithConstInterference(), 'Linear':Linear(), 'VillQintr':VillQintr(), 'Power':Power()}    
    return fitFct

class Generic_Fct():
    """
    This is a general class including all the basic functions for a fct.
    
    Any inheritance of this class should include the following overide the
    following methods:
        getParamList(self)
        applyEq(self, p, x)
    """
    def __init__(self):
        return
        
    def getParamList(self):
        """
        Overide this method to return the parameters specific to a fct
        """
        print("You need to Overwrite this in the specific function class")
        return None
        
    def applyEq(self, p, x):
        """
        Overide this method to return the parameters specific to a fct
        """
        print("You need to Overwrite this in the specific function class")
        return None
        
    def getLatex(self):
        """
        You should overwrite this to return the latex code for your equation
        """
        return 'No TeX Defined'
        
    def guessP(self, x, y):
        """
        You should overwrite this to return guess values for the parametera
        """
        return None
        
    def adjust(self, p):
        """
        You should overwrite this if you need to make adjustments to the parameter.
        For example, make and angle between 0 to 2pi...
        Overwriting this is optional.
        """
        return p
        
    def calcOutput(self, p):
        """
        You should overwrite this if you want to calculate other derived values
        from the parameters 'p'
        """
        return None
        
    def performFit(self, p, data, const = {}, repeat=1, errorMethod = "subtract"):
        """
        This is the function to call to perform a fit on the 'data' (tupple of 2
        1d-numpy array (x,y)) and a corresponding guess of parameters 'p'.
        Setting 'repeat' to an interger higher than 1 will redo the fit multiple times
        using the result of the previous fit as the guess for the next.
        'p' should be a dictionary with all the parameters (except the ones in const)
        required for the function (self.getParamList() will return that list).
        'const' should be a dictionary with all the parameters needed for the fct
        that should not be used for the function fitting.
        
        Returns the fitted function as a 1d numpy array and the assotiated parameters.
        """
        
        #Checks that repeat is a valid int
        if type(repeat)!=int or repeat<1:
            print("'repeat' must be an int greater or equal to 1")
            return None
            
        #Check that the parameters are all there and create an ordered ndarray
        pList = self.getParamList()
        pArray = []
        for param in pList:
            #Check that the parameters is present
            if param not in p and param not in const:
                print(("Missing parameter: "+param))
                return None
            #If it is a parameter to guess add it to the array
            elif param in p:
                pArray.append(p[param])
                
        p = _np.array(pArray)
                
        #Assign the x data
        x = data[0]
        y = data[1]
    
        
        #Repeat the fit for 'repeat' number of times
        plsq = [p]
        for i in range(0,repeat):
            #Do the fitting routine
            plsq = leastsq(self._residuals, plsq[0], args=(x,y, const, errorMethod))
        
        #Get the complete set of parameters including the constants
        p = self._replaceConst(plsq[0], const, pList)
        
        #Convert back to dict
        returnP = dict()
        for i in range(0,len(p)):
            returnP[pList[i]] = p[i]
            
        #Make specific adjustements if necessary
        returnP = self.adjust(returnP)
             
        return (x,self.applyEq(p, x)), returnP
        
    def _replaceConst(self, p, const, pList):
        """
        Generate the correct list of parameters taking in the p and the constant
        """
        #Figure out which parameters are constants and which are fitting parameters
        tempP = []
        nextP = 0
        for i in range(len(pList)):
            if pList[i] in list(const.keys()):
                tempP.append(const[pList[i]])
            else:
                tempP.append(p[nextP])
                nextP += 1
                
        return _np.array(tempP)
    
    allowedErrorMethods = ['subtract','cross_corr','subtract_square','exp_weigth']
    def _residuals(self, p, x, y, constant = {}, method = "subtract"):
        """
        Function to minimize with the fitting
        method availables are 'cross_corr' Cross correlation
        and 'subtract' image subtraction
        """
        
        #Get the right p
        pList = self.getParamList()
        p = self._replaceConst(p, constant, pList)    
    
        #This is the result of the fit with p
        fit = self.applyEq(p, x)
        
        #This calculates the residual in different ways
        if method=='subtract':
            res = fit-y
        elif method == 'cross_corr':
            res = (fit-y)-(fit*y)
        elif method == 'subtract_square':
            res = fit**2-y**2
        elif method == 'exp_weigth':
            res = _np.exp(fit)*(fit-y)
        
        #Reshape the 2D array to a 1D array to allow the lsqr to work properly
        #res = res.reshape(-1)
        return res
        
    def evaluateFct(self, p, x):
        """
        This methods allow you to evaluate the function with parameter p (can
        be a dict) for any x array
        """
        #Convert a dictionary to list if necessary
        if type(p)==dict:
            temp = list()
            for name in self.getParamList():
                temp.append(p[name])
            p = temp
        
        #Apply and return the result
        return self.applyEq(p, x)
                
            
        
#------------------------------------------------------------------------------
#                       LAURENTZIAN function
#------------------------------------------------------------------------------        
        
        
class Laurentzian(Generic_Fct):
    """
    This class inherits from the generic_fct class.
    
    It implements the following equation:
        fit = P*(gamma/(2pi))/((x-x0)^2+(0.5gamma)^2)+y0
        
    The required parameters for this fit are:
        ['P','x0', 'y0', 'gamma']
    """
    
    def __init__(self):
        return
        

    def getParamList(self):
        """
        This returns the parameters for this fct.
        ie. return ['P','x0', 'y0', 'gamma']
        """
        pList = ['P','x0', 'y0', 'gamma']           
        return pList
        
        
    def applyEq(self, p, x):
        """
        Apply the function with parameter p over x
        """
        #Unpack the parameters
        P, x0, y0, gamma = p
        
        #Apply the fct
        fit = P*(gamma/(2*_np.pi))/((x-x0)**2+(gamma/2)**2)+y0                   
            
        return fit
        
    def getLatex(self):
        """
        Returns the LaTeX version of the equation
        """
        return r'$y=P\left(\frac{\Gamma}{2\pi}\right)\frac{1}{\left(x-x_{0}\right)^{2}+\left(\frac{\Gamma}{2}\right)^{2}}+y_{0}$'
 
 
    def guessP(self, x, y):
        """
        Guess initial parameters p.
        x and y are the data to use for a guess
        """
        #Check that x and y are of same dimensions
        if x.shape != y.shape:
            print("X and Y arrays need to be of equal shape...")
            return None
        
        #Guess x0 and y0 very simply
        x0 = x[_np.argmax(y)]
        y0 = _np.min(y)
        
        #Guess linewidth
        max_y = _np.max(y)
        i = (_np.abs(_np.abs(y-max_y)-_np.abs(y-y0))).argmin()
        gamma = _np.abs((x[i]-x0)*2)
        
        #Guess the amplitude
        P = max_y*_np.pi*gamma/2
        
        
        
        return {'x0':x0, 'P':P, 'y0':y0, 'gamma':gamma}
        
        
    def calcOutput(self, p):
        """
        You should overwrite this if you want to calculate other derived values
        from the parameters 'p'
        """
        outputVal = dict()
        outputVal['Q'] = p['x0']/p['gamma']
        outputVal['f0'] = p['x0']
        outputVal['y0'] = p['y0']
        outputVal['Power'] = p['P']
        outputVal['Linewidth'] = p['gamma']
        
        return outputVal


#------------------------------------------------------------------------------
#                       GAUSSIAN function
#------------------------------------------------------------------------------
       

class Gaussian(Generic_Fct):
    """
    This class inherits from the generic_fct class.
    
    It implements the following equation:
        fit = A*exp(-0.5*((x-x0)/sigma)^2)+y0
        
    The required parameters for this fit are:
        ['A','x0', 'y0', 'sigma']
    """
    
    def __init__(self):
        return
        

    def getParamList(self):
        """
        This returns the parameters for this fct.
        ie. return ['P', 'x0', 'y0', 'sigma']
        """
        pList = ['P', 'x0', 'y0', 'sigma']          
        return pList
        
        
    def applyEq(self, p, x):
        """
        Apply the function with parameter p over x
        """
        
        #Unpack the parameters
        P, x0, y0, sigma = p
        
        #Apply the fct
        fit = P*(1/(sigma*_np.sqrt(2*_np.pi)))*_np.exp(-0.5*((x-x0)/sigma)**2)+y0              
        return fit
        
    def getLatex(self):
        """
        Returns the LaTeX version of the equation
        """
        return r'$y=\left(\frac{P}{\sigma\sqrt{2\pi}}\right)e^{\frac{-(x-x_{0})^{2}}{2\sigma^{2}}}+y_{0}$'
   
   
    def guessP(self, x, y):
        """
        Guess parametters list for this function
        """
        #Guess the mean of the distribution
        x0 = x[_np.argmax(y)]

        #Guess the std dev of the distribution
        max_y = _np.max(y)
        y0 = _np.min(y)
        i = (_np.abs((y-y0)-(max_y-y0)*_np.exp(-1))).argmin()
        sigma = _np.abs((x[i]-x0))
        
        #Guess the power
        print(max_y)
        print(sigma)
        P = (max_y-y0)*sigma*_np.sqrt(2*_np.pi)
        print(P)
        
        return {'x0':x0, 'P':P, 'sigma':sigma, 'y0':y0}
        
#------------------------------------------------------------------------------
#                   LAURENTZIAN WITH CONSTANT INTERFERENCE function
#------------------------------------------------------------------------------        
        
class LaurentzianWithConstInterference(Generic_Fct):
    """
    This class inherits from the generic_fct class.
    
    It implements the following equation:
        y=\frac{2PA\left(\left(x_{0}^{2}-x^{2}\right)\cos\phi+2\Gamma x\sin\phi\right)}{4\Gamma_{m}^{2}\Omega^{2}+\left(x^{2}-x_{0}^{2}\right)^{2}}+A^{2}
        
    The required parameters for this fit are:
        ['P','x0', 'gamma', 'A', 'phi']
    """
    
    def __init__(self):
        return
        

    def getParamList(self):
        """
        This returns the parameters for this fct.
        ie. return ['P','x0', 'gamma', 'A', 'phi']
        """
        pList = ['P','x0', 'gamma', 'A', 'phi']          
        return pList
        
        
    def applyEq(self, p, x):
        """
        Apply the function with parameter p over x
        """
        
        #Unpack the parameters
        P, x0, gamma, A, phi = p
        
        #Apply the fct
        #num = P + _np.sqrt(P)*(2*Ar*(x0**2-x**2)-4*Ai*gamma*x)
        #num = P**2 + 2*P*A*((x0**2-x**2)*_np.cos(phi)-2*gamma*x*_np.sin(phi))
        num = 2*P*A*((x0**2-x**2)*_np.cos(phi)-2*gamma*x*_np.sin(phi))        
        #den = 4*(gamma**2)*(x0**2)+(x0**2-x**2)**2
        den = 1+ ((x0-x)**2)/((gamma**2))
        preF = (4*(gamma**2)*(x0**2))**-1
        fit = preF*(num/den)+A**2
                        
        return fit
        
    def getLatex(self):
        """
        Returns the LaTeX version of the equation
        """
        return r'$y=\frac{2PA\left(\left(x_{0}^{2}-x^{2}\right)\cos\phi+2\Gamma x\sin\phi\right)}{4\Gamma_{m}^{2}\Omega^{2}+\left(x^{2}-x_{0}^{2}\right)^{2}}+A^{2}$'
 
 
    def guessP(self, x, y):
        """
        Guess initial parameters p.
        x and y are the data to use for a guess
        """
        #Check that x and y are of same dimensions
        if x.shape != y.shape:
            print("X and Y arrays need to be of equal shape...")
            return None
        
        #Guess x0 and y0 very simply
        x0 = x[int(_np.argmax(y)+_np.argmin(y)/2)]
        A = _np.sqrt(_np.mean(y))
        
        #Guess linewidth
        gamma = _np.abs(x[_np.argmax(y)]-x[_np.argmin(y)])/2
        
        #Guess the angle
        
#        
#        #Guess the amplitude
#        P = max_y*_np.pi*gamma/2
        
        
        
        return {'x0':x0, 'A':A, 'gamma':gamma}
        
    def adjust(self, p):
        """
        This adjust the phi angle so it is between 0 and 2pi
        """
        p['phi']= _np.mod(p['phi'], 2*_np.pi)
        return p
        
        
#------------------------------------------------------------------------------
#                            COSINE function
#------------------------------------------------------------------------------

class Cos(Generic_Fct):
    """
    This class inherits from the generic_fct class.
    
    It implements the following equation:
        fit = A*cos(2*pi*f*x+phi)+B
        
    The required parameters for this fit are:
        ['A','B','f','phi']
    """
    
    def __init__(self):
        return
        

    def getParamList(self):
        """
        This returns the parameters for this fct.
        ie. return ['A','y0','f','phi']
        """
        pList = ['A','y0','f','phi']            
        return pList
        
        
    def applyEq(self, p, x):
        """
        Apply the function with parameter p over x
        """
        #Unpack the parameters
        A, y0, f, phi = p
        
        #Apply the fct
        fit = A*_np.cos(2*_np.pi*f*x+phi)+y0                    
            
        return fit
        
    def getLatex(self):
        return r'$y=A\cdot\cos\left(2\pi f\cdot x+\phi\right)+y_{0}$'     

#------------------------------------------------------------------------------
#                       LINEAR function
#------------------------------------------------------------------------------        
 
        
class Linear(Generic_Fct):
    def getParamList(self):
        return ['m','b']
        
    def applyEq(self, p, x):
        #Unpack the parameters
        m, b = p
        #Apply the fct
        return m*x+b
        
    def guessP(self, x, y):
        #Guess a
        m = (y[0]-y[-1])/(x[0]-x[-1])
        #Guess b
        b = y[0]-m*x[0]
        return {'m':m, 'b':b}
        
    def getLatex(self):
        return r'$y=mx+b$'
        
    def calcOutput(self, p):
        outVal = p
        return outVal
        

#------------------------------------------------------------------------------
#                       POWER function
#------------------------------------------------------------------------------  

class Power(Generic_Fct):
    
    def getParamList(self):          
        return ['A','y','B']
             
    def applyEq(self, p, x):
        #Unpack the parameters
        A,y,B = p
        #Apply the fct
        fit = A*x**y+B              
        return fit























#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#                   Quick Tests (maybe wrong equations)
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


#------------------------------------------------------------------------------
#                       RESONANCE function
#------------------------------------------------------------------------------        
 
        
class Resonance(Generic_Fct):
    def getParamList(self):          
        return ['P','x0', 'y0', 'gamma']
             
    def applyEq(self, p, x):
        #Unpack the parameters
        P, x0, y0, gamma = p
        #Apply the fct
        fit = ((P*(gamma/(2*_np.pi))/((x**2-x0**2)**2+(x*gamma/2)**2))**-1+y0**-1)**-1                
        return fit
        
    def getLatex(self):
        return r'$y=P\left(\frac{\Gamma}{2\pi}\right)\frac{1}{\left(x^{2}-x_{0}^{2}\right)^{2}+\left(x\frac{\Gamma}{2}\right)^{2}}+y_{0}$'
 
 
    def guessP(self, x, y):
        #Check that x and y are of same dimensions
        if x.shape != y.shape:
            print("X and Y arrays need to be of equal shape...")
            return None
        #Guess x0 and y0 very simply
        x0 = x[_np.argmax(y)]
        y0 = _np.min(y)
        
        #Guess linewidth
        max_y = _np.max(y)
        i = (_np.abs(_np.abs(y-max_y)-_np.abs(y-y0))).argmin()
        gamma = _np.abs((x[i]-x0)*2)
        
        #Guess the amplitude
        P = max_y*_np.pi*gamma/2
        return {'x0':x0, 'P':P, 'y0':y0, 'gamma':gamma}  
        
    def calcOutput(self, p):
        outputVal = dict()
        outputVal['Q'] = p['x0']/p['gamma']
        outputVal['f0 in MHz'] = p['x0']/1e6
        outputVal['y0'] = p['y0']
        outputVal['Power'] = p['P']
        outputVal['Linewidth'] = p['gamma']
        return outputVal
        
        
#------------------------------------------------------------------------------
#                       VILLANUAVA MODEL FOR INTRINSIC Q
#------------------------------------------------------------------------------        
 
        
class VillQintr(Generic_Fct):
    def getParamList(self):          
        return ['Qintr','E', 'sigma', 'h', 'L']
             
    def applyEq(self, p, x):
        #Unpack the parameters
        Qintr, E, sigma, h, L = p
        #Apply the fct
        _lambda = _np.sqrt((1.0/12.0)*(E/sigma)*(h/L)**2)
        fit = Qintr*(2*_lambda+(x*_np.pi*_lambda)**2)**(-1)             
        return fit
        
    def getLatex(self):
        return r'$Q=\frac{Q_{intr}}{\left(2\lambda+\left(x\pi\lambda\right)^{2}\right)}$, $\lambda=\sqrt{\frac{1}{12}\frac{E}{\sigma}\frac{h^{2}}{L^{2}}}$'
 
 
    def guessP(self, x, y):
        return {'Qintr':4400,'E':200e9, 'sigma':800e6, 'h':100e-9, 'L':50e-6}  
        
    def calcOutput(self, p):
        outputVal = dict()
        outputVal['lambda'] = _np.sqrt((1.0/12.0)*(p['E']/p['sigma'])*(p['h']/p['L'])**2)
        return outputVal
        
