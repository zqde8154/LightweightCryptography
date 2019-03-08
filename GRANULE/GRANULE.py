import numpy

#-----------------------------------------Boxes---------------------------------------------
# Definition of the SBOX, used in sbox_layer method and in generate_round_keys
SBOX = [14, 7, 8, 4, 1, 9, 2, 15, 5, 10, 11, 0, 6, 12, 13, 3]

# Definition of the PBOX, used in pbox_layer
PBOX_2 = [4, 0, 3, 1, 6, 2, 7, 5]
PBOX = [2, 0, 5, 1, 6, 4, 7, 3]

ROUNDS = 32
#-------------------------------------------------------------------------------------------

#--------------------------------------Key schedule-----------------------------------------
#-------------------------Generated keys----------------------------
def round_keys(key):
	keys = []    #Here save the key generated by update

	for i in range(ROUNDS):    #Generate 32 keys of 128 bits
		c, key = update_key(key, i)    #update the key, this returns the key update and 
		keys.append(c)                 #append the generated key 

	return keys
#--------------------------------------------------------------------

#--------------------------------------------------------------------
# Method that updates the key, in each iteration of generate_round_keys method
def update_key(current_key, round_counter):
    #-----------Left Rotation of 31 bits----------
	new_key = numpy.roll(current_key, -31)
    #---------------------------------------------

    #--------k3,k2,k1,k0 <- S(k3,k2,k1,k0)------------- 
	sbox_index = get_fragment_int(new_key, 124, 128)
	new_key[124:128] = int_to_bin(SBOX[sbox_index], 4)
    #--------------------------------------------------

    #--------k7,k6,k5,k4 <- S(k7,k6,k5,k4)------------- 
	sbox_index = get_fragment_int(new_key, 120, 124)
	new_key[120:124] = int_to_bin(SBOX[sbox_index], 4)
    #--------------------------------------------------

    #---[k70,k69,k68,k67,k66] <- [k70,k69,k68,k67,k66]XOR[i]^2---
	chunk = get_fragment_int(new_key, 57, 62)
	new_key[57:62] = int_to_bin(chunk ^ (round_counter % 32), 5)
    #------------------------------------------------------------

	return list(current_key)[-32:], list(new_key)
    #--------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

#---------------------------------------Encrypt---------------------------------------------
#------------------------------------------------------------
def Encrypt(plaintext, keys):
	# Plaintext is divided in two
	pt1 = plaintext[0:32]
	pt0 = plaintext[32:]

	# 32 rounds of the algorithm
	for i in range(ROUNDS):
		#print i
		# Execution of f function
		f_return  = f_function(pt1)

		# Add round key operation
		#print "pt0", pt0
		#print "key", keys[i]
		temp = add_round_key(pt0, f_return, keys[i])
		#print "temp", temp
		
		"""
		print i
		print "pt0", pt0
		print "ptX", pt1
		print "f_r", f_return
		print "kys", keys[i]
		print "............"
		"""

		# Exchange position of the chunks
		pt0 = pt1
		pt1 = temp

	return pt1+pt0
#------------------------------------------------------------

#------------------------------------------------------------
def f_function(pt1):
	# First. p_layer
	new_state = p_layer2(pt1)

	# Then, sbox_layer
	new_state = sbox_layer(new_state)

	# Next step, rp_layer
	new_state = rp_layer(new_state)

	return new_state
#------------------------------------------------------------

#------------------------------------------------------------
# Operation: p_layer
def p_layer(state):
	new_state = [0] * 32

	# Permutation of all the bits, according to pbox
	for i in range(len(new_state) / 4):
		mark = PBOX[i]
		offset = mark * 4
		state_offset =  i * 4
		new_state[offset:offset + 4] = state[state_offset:state_offset + 4]

	return new_state
#------------------------------------------------------------

#------------------------------------------------------------
def p_layer2(state):
	new_state = [0] * 32
	#aux = int(len(new_state) / 4)
	for i in range(8):
		mark = PBOX_2[i]
		offset = mark * 4;
		ns_o = 4 * i
		new_state[ns_o:ns_o+4] = state[offset:offset+4]

	return new_state
#------------------------------------------------------------

#------------------------------------------------------------
# Operation: sbox_layer
def sbox_layer(state):
	# Each nibble enters into the SBOX
	for i in range(8):
		# Offset in each nibble
		beg = 4 * i
		
		# Convert bin to dec
		sbox_index = get_fragment_int(state, beg, beg + 4)
		
		# SBOX operation
		state[beg:beg+4] = int_to_bin(SBOX[sbox_index], 4)

	return state
#------------------------------------------------------------

#------------------------------------------------------------
def rp_layer(state):
	# Two rotation
	temp0 = numpy.roll(state, -2)
	temp1 = numpy.roll(state, 7)
	
	# X-OR between the last operations
	y = temp0 ^ temp1

	return y.tolist()
#------------------------------------------------------------

#------------------------------------------------------------
# Operation: add_round_key
def add_round_key(pt0, f_ret, key):
	new_state = []

	# X-OR operation, bit per bit.
	for i in range(len(pt0)): 
		new_state.append(pt0[i] ^ f_ret[i] ^ key[i])

	return new_state
#------------------------------------------------------------
#-------------------------------------------------------------------------------------------

#---------------------------------------Decrypt---------------------------------------------
#------------------------------------------------------------
def Decrypt(ciphertext, keys):
	# It is necessary to exchange position, due to how the cipher text is entered
	pt0 = ciphertext[0:32]
	pt1 = ciphertext[32:]

	# 32 rounds of the algorithm
	for i in range(ROUNDS):
		# Execution of f funcion
		f_return  = f_function(pt1)	

		# Add round key operation	
		temp = add_round_key(pt0, f_return, keys[ROUNDS - 1 - i])

		# Exchange position of the chunks
		pt0 = pt1
		pt1 = temp

	return pt0+pt1
#------------------------------------------------------------
#-------------------------------------------------------------------------------------------

#-----------------------------------Auxiliar Functions--------------------------------------
def get_fragment_int(array, begin, end):
	return int("".join(map(str, array[begin:end])), 2)

def int_to_bin(number, w):
	return list(map(int, numpy.binary_repr(number, width=w)))

def pretty_print(array):
	_str = ""

	for i in range(0, 64, 4):
		_str += hex(get_fragment_int(array, i, i + 4)).split('0x')[1]

	return _str

def pretty_printK(array):
	_str = ""

	for i in range(0, 128, 4):
		_str += hex(get_fragment_int(array, i, i + 4)).split('0x')[1]
	return _str

#-------------------------------------------------------------------------------------------


if __name__ == '__main__':
	plaintext = [1]*64
	k = [1]*128

	keys = round_keys(k)

	ciphertext = Encrypt(plaintext, keys)

	newplaintext = Decrypt(ciphertext, keys)

	print("plaintext     = ", pretty_print(newplaintext))
	print("ciphertext    = ", pretty_print(ciphertext))
	print("key    = ", pretty_printK(k))
	print("Desciphertext = ", pretty_print(newplaintext))
