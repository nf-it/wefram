import React from 'react'
import {ProjectSidebar, ProjectScreens} from 'build/components'


const ProjectLayout = () => (
  <div style={{
    display: 'flex'
  }}>
    <ProjectSidebar />
    <ProjectScreens />
  </div>
)

export default ProjectLayout
