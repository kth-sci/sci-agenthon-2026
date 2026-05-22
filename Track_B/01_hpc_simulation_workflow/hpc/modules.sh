#!/usr/bin/env bash
# =============================================================================
# EXAMPLE module setup — TEMPLATE ONLY.
#
# The module names below are generic placeholders, not real site modules. Replace them
# with the modules your cluster actually provides (check your site's documentation).
# This file is meant to be inspected and adapted, not run locally.
# =============================================================================

module purge
module load python/3.11        # EXAMPLE module name
module load numpy              # EXAMPLE — often provided via python or a virtual env

# Alternatively, activate a prepared virtual environment, e.g.:
# source "$HOME/envs/oscillator/bin/activate"
