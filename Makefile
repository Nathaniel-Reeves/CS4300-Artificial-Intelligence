#
# Expects to be used when a Python environment has been activated
#
VENV := .venv
#######################################################################
#
# if the virtual environment has not been activated
#
#######################################################################
ifeq ($(VIRTUAL_ENV),)
all install: $(VENV) 
	@echo "Remember to start your virtual environment with "
	@echo "  source $(VENV)/bin/activate"

$(VENV):
	@echo "You need to make the virtual environment: "
	@echo "    python3 -m venv $(VENV)"

#######################################################################
#
# if the virtual environment has been activated
#
#######################################################################
else
all:
	@echo make install to install all python packages


install: install-pip

install-pip:
	pip3 install -r requirements.txt


#######################################################################
#
# end if 
#
#######################################################################
endif
