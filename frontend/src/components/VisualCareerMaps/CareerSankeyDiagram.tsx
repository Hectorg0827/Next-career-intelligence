'use client';

import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * FEATURE 5: Visual Career Maps - Sankey Diagram
 * 
 * Interactive career pathway visualization showing multiple possible futures
 * with branching paths, skill requirements, and confidence scores.
 */

interface SankeyNode {
  id: number;
  name: string;
  category: 'current' | '3-year' | '3-year-alt' | '5-year' | '5-year-alt' | '10-year' | '10-year-alt';
}

interface SankeyLink {
  source: number;
  target: number;
  value: number;
  skill: string;
}

interface SankeyData {
  nodes: SankeyNode[];
  links: SankeyLink[];
}

interface CareerSankeyDiagramProps {
  data: SankeyData;
  currentRole: string;
}

export default function CareerSankeyDiagram({ data, currentRole }: CareerSankeyDiagramProps) {
  const [selectedNode, setSelectedNode] = useState<number | null>(null);
  const [hoveredLink, setHoveredLink] = useState<number | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Calculate node positions (horizontal timeline layout)
  const getNodePosition = (node: SankeyNode) => {
    const width = 800;
    const height = 600;
    
    let x = 0;
    if (node.category === 'current') x = 50;
    else if (node.category.includes('3-year')) x = 250;
    else if (node.category.includes('5-year')) x = 450;
    else if (node.category.includes('10-year')) x = 650;
    
    let y = height / 2;
    if (node.category.includes('-alt')) y += 120;
    else if (!node.category.includes('current')) y -= 60;
    
    return { x, y };
  };

  // Calculate link path (curved bezier)
  const getLinkPath = (link: SankeyLink) => {
    const sourceNode = data.nodes.find(n => n.id === link.source);
    const targetNode = data.nodes.find(n => n.id === link.target);
    
    if (!sourceNode || !targetNode) return '';
    
    const start = getNodePosition(sourceNode);
    const end = getNodePosition(targetNode);
    
    const midX = (start.x + end.x) / 2;
    
    return `M ${start.x + 80} ${start.y} 
            C ${midX} ${start.y}, 
              ${midX} ${end.y}, 
              ${end.x} ${end.y}`;
  };

  const getCategoryColor = (category: string) => {
    if (category === 'current') return 'from-gray-600 to-gray-700';
    if (category.includes('3-year')) return 'from-green-500 to-emerald-600';
    if (category.includes('5-year')) return 'from-blue-500 to-indigo-600';
    if (category.includes('10-year')) return 'from-purple-500 to-pink-600';
    return 'from-gray-400 to-gray-500';
  };

  const getStrokeColor = (value: number) => {
    if (value >= 80) return 'rgba(34, 197, 94, 0.4)'; // Green
    if (value >= 60) return 'rgba(59, 130, 246, 0.4)'; // Blue
    if (value >= 40) return 'rgba(168, 85, 247, 0.4)'; // Purple
    return 'rgba(156, 163, 175, 0.3)'; // Gray
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-bold text-gray-900">
            📊 Visual Career Map
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Interactive pathway showing your possible futures
          </p>
        </div>
        
        {/* Legend */}
        <div className="flex items-center gap-4 text-xs text-gray-600">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-gradient-to-r from-green-500 to-emerald-600"></div>
            <span>3 Years</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600"></div>
            <span>5 Years</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-gradient-to-r from-purple-500 to-pink-600"></div>
            <span>10 Years</span>
          </div>
        </div>
      </div>

      {/* SVG Visualization */}
      <div 
        ref={containerRef}
        className="bg-gradient-to-br from-gray-50 via-white to-blue-50 rounded-2xl border-2 border-gray-200 overflow-hidden"
      >
        <svg 
          width="100%" 
          height="600" 
          viewBox="0 0 800 600"
          className="overflow-visible"
        >
          {/* Links/Paths */}
          <g className="links">
            {data.links.map((link, index) => (
              <motion.g
                key={`link-${index}`}
                initial={{ opacity: 0, pathLength: 0 }}
                animate={{ opacity: 1, pathLength: 1 }}
                transition={{ delay: index * 0.1, duration: 1 }}
              >
                {/* Path */}
                <motion.path
                  d={getLinkPath(link)}
                  fill="none"
                  stroke={getStrokeColor(link.value)}
                  strokeWidth={link.value / 5}
                  className="transition-all cursor-pointer"
                  onMouseEnter={() => setHoveredLink(index)}
                  onMouseLeave={() => setHoveredLink(null)}
                  style={{
                    filter: hoveredLink === index ? 'brightness(1.5)' : 'none',
                    strokeWidth: hoveredLink === index ? link.value / 3 : link.value / 5
                  }}
                />
                
                {/* Skill label on hover */}
                {hoveredLink === index && (
                  <motion.text
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    x={(getNodePosition(data.nodes[link.source]).x + getNodePosition(data.nodes[link.target]).x) / 2}
                    y={(getNodePosition(data.nodes[link.source]).y + getNodePosition(data.nodes[link.target]).y) / 2}
                    textAnchor="middle"
                    className="text-xs font-semibold fill-gray-700"
                  >
                    {link.skill}
                    <tspan x={(getNodePosition(data.nodes[link.source]).x + getNodePosition(data.nodes[link.target]).x) / 2} dy="15" className="text-xs font-normal fill-gray-600">
                      {link.value}% confidence
                    </tspan>
                  </motion.text>
                )}
              </motion.g>
            ))}
          </g>

          {/* Nodes */}
          <g className="nodes">
            {data.nodes.map((node) => {
              const pos = getNodePosition(node);
              const isSelected = selectedNode === node.id;
              const isConnected = selectedNode !== null && data.links.some(
                l => (l.source === selectedNode && l.target === node.id) || 
                     (l.target === selectedNode && l.source === node.id)
              );

              return (
                <motion.g
                  key={`node-${node.id}`}
                  initial={{ opacity: 0, scale: 0 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: node.id * 0.15, type: 'spring' }}
                  onClick={() => setSelectedNode(isSelected ? null : node.id)}
                  className="cursor-pointer"
                  style={{
                    filter: selectedNode === null || isSelected || isConnected ? 'none' : 'grayscale(70%) opacity(0.4)'
                  }}
                >
                  {/* Node background */}
                  <rect
                    x={pos.x}
                    y={pos.y - 25}
                    width={160}
                    height={50}
                    rx={12}
                    className={`fill-gradient-to-r ${getCategoryColor(node.category)}`}
                    style={{
                      fill: `url(#gradient-${node.id})`,
                      filter: isSelected ? 'drop-shadow(0 4px 20px rgba(0,0,0,0.3))' : 'drop-shadow(0 2px 8px rgba(0,0,0,0.1))'
                    }}
                  />
                  
                  {/* Gradient definition */}
                  <defs>
                    <linearGradient id={`gradient-${node.id}`} x1="0%" y1="0%" x2="100%" y2="0%">
                      {node.category === 'current' && (
                        <>
                          <stop offset="0%" style={{ stopColor: '#4B5563' }} />
                          <stop offset="100%" style={{ stopColor: '#374151' }} />
                        </>
                      )}
                      {node.category.includes('3-year') && (
                        <>
                          <stop offset="0%" style={{ stopColor: '#10B981' }} />
                          <stop offset="100%" style={{ stopColor: '#059669' }} />
                        </>
                      )}
                      {node.category.includes('5-year') && (
                        <>
                          <stop offset="0%" style={{ stopColor: '#3B82F6' }} />
                          <stop offset="100%" style={{ stopColor: '#4F46E5' }} />
                        </>
                      )}
                      {node.category.includes('10-year') && (
                        <>
                          <stop offset="0%" style={{ stopColor: '#A855F7' }} />
                          <stop offset="100%" style={{ stopColor: '#EC4899' }} />
                        </>
                      )}
                    </linearGradient>
                  </defs>

                  {/* Node text */}
                  <text
                    x={pos.x + 80}
                    y={pos.y}
                    textAnchor="middle"
                    className="text-xs font-bold fill-white pointer-events-none"
                  >
                    {node.name.length > 20 ? node.name.substring(0, 18) + '...' : node.name}
                  </text>
                  
                  {/* Year badge */}
                  {node.category !== 'current' && (
                    <text
                      x={pos.x + 80}
                      y={pos.y + 12}
                      textAnchor="middle"
                      className="text-[10px] fill-white opacity-80 pointer-events-none"
                    >
                      {node.category.includes('3-year') ? 'Year 3' : 
                       node.category.includes('5-year') ? 'Year 5' : 'Year 10'}
                    </text>
                  )}

                  {/* Selection indicator */}
                  {isSelected && (
                    <motion.circle
                      cx={pos.x + 80}
                      cy={pos.y}
                      r={30}
                      fill="none"
                      stroke="white"
                      strokeWidth={2}
                      initial={{ scale: 0 }}
                      animate={{ scale: 1.2 }}
                      transition={{ duration: 0.3 }}
                    />
                  )}
                </motion.g>
              );
            })}
          </g>

          {/* Timeline axis */}
          <g className="timeline">
            <line x1={50} y1={550} x2={730} y2={550} stroke="#E5E7EB" strokeWidth={2} />
            <text x={50} y={570} className="text-xs fill-gray-500 font-medium">Today</text>
            <text x={250} y={570} className="text-xs fill-gray-500 font-medium">3 Years</text>
            <text x={450} y={570} className="text-xs fill-gray-500 font-medium">5 Years</text>
            <text x={650} y={570} className="text-xs fill-gray-500 font-medium">10 Years</text>
          </g>
        </svg>
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
        <p className="text-sm text-blue-900">
          <strong>💡 How to use:</strong> Click nodes to highlight connections • Hover over paths to see required skills • 
          Thicker lines = higher confidence • Alternative paths shown below primary progression
        </p>
      </div>

      {/* Selected node details */}
      <AnimatePresence>
        {selectedNode !== null && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-200 rounded-xl p-6"
          >
            <h4 className="text-lg font-bold text-purple-900 mb-3">
              {data.nodes.find(n => n.id === selectedNode)?.name}
            </h4>
            
            {/* Incoming paths */}
            <div className="mb-4">
              <p className="text-sm font-semibold text-purple-800 mb-2">📥 How to get here:</p>
              <div className="space-y-2">
                {data.links
                  .filter(l => l.target === selectedNode)
                  .map((link, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm text-purple-700">
                      <span className="px-2 py-1 bg-white rounded-lg font-medium">
                        {link.skill}
                      </span>
                      <span className="text-xs text-purple-600">
                        ({link.value}% confidence)
                      </span>
                    </div>
                  ))}
              </div>
            </div>

            {/* Outgoing paths */}
            <div>
              <p className="text-sm font-semibold text-purple-800 mb-2">📤 Where this leads:</p>
              <div className="space-y-2">
                {data.links
                  .filter(l => l.source === selectedNode)
                  .map((link, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm text-purple-700">
                      <span>→</span>
                      <span className="font-medium">
                        {data.nodes.find(n => n.id === link.target)?.name}
                      </span>
                      <span className="text-xs text-purple-600">
                        via {link.skill}
                      </span>
                    </div>
                  ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
