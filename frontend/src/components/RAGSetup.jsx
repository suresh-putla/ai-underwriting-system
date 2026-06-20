import React, { useState } from 'react'
import RAGConfiguration from './RAGConfiguration'
import RAGChat from './RAGChat'
import RAGLLMChat from './RAGLLMChat'

const RAGSetup = () => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Tile 1: RAG Configuration */}
      <RAGConfiguration />

      {/* Tile 2: RAG Search */}
      <RAGChat />

      {/* Tile 3: RAG Search + LLM */}
      <RAGLLMChat />
    </div>
  )
}

export default RAGSetup
