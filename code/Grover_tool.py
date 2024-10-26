from qiskit.circuit import QuantumCircuit
from qiskit.primitives import Sampler
import numpy as np
from qiskit.quantum_info import Statevector
from qiskit.primitives import StatevectorSampler
from qiskit.visualization import plot_histogram
import math

def diffusion(qc:QuantumCircuit,n:int):
    """
    Perform a quantum diffusion operation, which is a key step in the Grover's algorithm used to amplify the amplitude of the target state.

    Parameters:
        qc (QuantumCircuit): The quantum circuit object on which the operation will be performed.
        n (int): The number of qubits, excluding the ancillary qubit.
    
    """

    qc.barrier(range(n))
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n-1)
    qc.barrier(range(n))
    qc.mcx(control_qubits=list(range(n-1)),target_qubit=n-1)
    qc.h(n-1)
    qc.barrier(range(n))
    qc.x(range(n))
    qc.h(range(n))

def oracle(qc: QuantumCircuit,n:int,good_states:np.array):
    """
    Define an Oracle operation to mark the target state in the quantum search algorithm.

    Parameters:
        qc (QuantumCircuit): The quantum circuit object on which the operation will be performed.
        n (int): The number of qubits, excluding the ancillary qubit.
        good_states (np.array): A list of target states, each state represented by a binary string.
    """
        
    for each_states in good_states:
        qc.mcx(control_qubits=list(range(n)),target_qubit=n,ctrl_state=''.join(each_states[::-1].astype(str))) 

def build_grover_circuit(n:int,initial_state:np.array,good_states:np.array,iterations:int=1):
    '''
    n: The number of qubits does not include auxiliary qubits
    
    '''
    qc = QuantumCircuit(n+1,n)
    Initialize(n,qc,initial_state)
    qc.x(n)
    qc.h(n)
    qc.barrier()
    for _ in range(iterations):
        oracle(qc,n,good_states)
        qc.barrier()
        diffusion(qc,n)
        qc.barrier()
    return qc

def Initialize(n:int,qc: QuantumCircuit,state:np.array):
    """
    Initialize the quantum circuit to the specified state.

    Parameters:
        n (int): The number of qubits.
        qc (QuantumCircuit): The quantum circuit object to be initialized.
        state (np.array): The initial state of the quantum circuit, represented as a binary array.
    """
    for index,each_bit in enumerate(state):
        if each_bit == 1:
            qc.x(index)
        else:
            qc.h(index)
        
class Grover:
    def __init__(self,initial_state:np.array,good_states: np.array,iterations:int=1) -> None:
        self.good_states = good_states
        self.iterations = iterations
        self.initial_state = initial_state
        self.sampler = StatevectorSampler()

        # keep the position where state is 0
        self.empty_edge = np.where(self.initial_state==0)[0]
        
        self.n_empty = len(self.empty_edge)
        self.theta = np.arcsin(np.sqrt(len(self.good_states)/2**self.n_empty))
        self.k = math.floor(np.pi/(4*self.theta)+1/2)
        
        # calculate theoretical win rate
        self.probability_win = np.sin((2*self.k+1)*self.theta)**2
        
        self._initial_state=[self.initial_state[index] for index,value in enumerate(self.initial_state) if index in self.empty_edge]
        
        self.index_ = np.where(self.initial_state==1)[0]
        self._good_states = []
        for each in self.good_states:
            result = [each[index] for index,value in enumerate(each) if index not in self.index_  ]
            self._good_states.append(result)
        self._good_states = np.array(self._good_states)
        self.num_qbits_activate = len(self._initial_state)
        
        #print(f'initial_state:{self._initial_state}')
        self.qc = build_grover_circuit(self.n_empty,self._initial_state,self._good_states,self.k)
        self.qc_one = build_grover_circuit(self.n_empty,self._initial_state,self._good_states,1)
        

        #self.get_probability()
        
    def get_probability(self):
        """
        Obtaining the probability of target state occurrence by measuring the qubits.
        """
        self.qc_measure = self.qc.copy()
        self.qc_measure.measure(range(self.n_empty),range(self.n_empty))

        result = self.sampler.run([self.qc_measure],shots=1024).result()
        self.result_dict = result[0].data.c.get_counts()
    
    def give_real_choice(self):
        """
        Only select once to provide a genuine choice
        """
        self.qc = build_grover_circuit(self.n_empty,self._initial_state,self._good_states,self.k)
        self.qc_one = build_grover_circuit(self.n_empty,self._initial_state,self._good_states,1)
        self.qc_measure = self.qc.copy()
        self.qc_measure.measure(range(self.n_empty),range(self.n_empty))
        result = self.sampler.run([self.qc_measure],shots=1).result()
        self.result_dict = result[0].data.c.get_counts()
        self.real_choice = list(self.result_dict.keys())[0]
    
        self.real_choice = list(self.real_choice)[::-1]
        for i in self.index_:
            self.real_choice.insert(i,'1')
        self.real_choice = np.array(self.real_choice,dtype=int)
        return self.real_choice
       
    def show_result(self):
        """
        Display measurement results, only showing results with more than 5 occurrences.
        """
        self.filtered_result = {k:v for k,v in self.result_dict.items() if v > 5}
        
        

        