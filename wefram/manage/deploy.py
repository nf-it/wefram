"""
Provides the facility to deploy the project from the management/
development layer to the production one.

This procedure prepares the neccessary deployment configurations
like *Dockerfile* and *requirements*, and copies enabled (and only
enabled) applications and system files to the deployment
target path.

Optionally, basing on the 'clean' configuration parameter, this
facility may remove all existing files from the deployment
target
"""



