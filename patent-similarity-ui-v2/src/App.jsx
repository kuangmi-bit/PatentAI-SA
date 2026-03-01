import React, { useState, useRef, useEffect, useCallback } from 'react'
import { BrowserRouter, Routes, Route, Link, useNavigate, useParams, useLocation } from 'react-router-dom'
import ApiTest from './ApiTest'
import api from './api.js'

// ==================== Icons ====================
const Icons = {
  // Navigation
  Home: ({ size = 20, color = 'currentColor' }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
      <polyline points="9 22 9 12 15 12 15 22"/>
    </svg>
  ),
  Tasks: ({ size = 20, color = 'currentColor' }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 11l3 3L22 4"/>
      <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
    </svg>
  ),
  Library: ({ size = 20, color = 'currentColor' }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
    </svg>
  ),
  // Stats
  Chart: ({ size = 20, color = 'currentColor' }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="20" x2="18" y2="10"/>
      <line x1="12" y1="20" x2="12" y2="4"/>
      <line x1="6" y1="20" x2="6" y2="14"/>
    </svg>
  ),
  Refresh: ({ size = 20, color = 'currentColor' }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="23 4 23 10 17 10"/>
      <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
    </svg>
  ),
  Check: ({ size = 20, color = 'currentColor' }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12"/>
    </svg>
  ),
  Alert: ({ size = 20, color = 'currentColor' }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
      <line x1="12" y1="9" x2="12" y2="13"/>
      <line x1="12" y1="17" x2="12.01" y2="17"/>
    </svg>
  ),
  AlertTriangle: ({ size = 20, color = 'currentColor' }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
      <line x1="12" y1="9" x2="12" y2="13"/>
      <line x1="12" y1="17" x2="12.01" y2="17"/>
    </svg>
  ),
  // Templates
  Target: ({ size = 20, color = 'currentColor' }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <circle cx="12" cy="12" r="6"/>
      <circle cx="12" cy="12" r="2"/>
    </svg>
  ),
  Lightbulb: ({ size = 20, color = 'currentColor' }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 18h6"/>
      <path d="M10 22h4"/>
      <path d="M12 2a7 7 0 0 0-7 7c0 2.5 1.5 4.5 3 6s2 3 2 4h4c0-1 .5-2.5 2-4s3-3.5 3-6a7 7 0 0 0-7-7z"/>
    </svg>
  ),
  Binoculars: ({ size = 20, color = 'currentColor' }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10 10h4v4h-4z"/>
      <path d="M10 6V4a2 2 0 0 1 4 0v2"/>
      <path d="M6 10H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2v-6a2 2 0 0 0-2-2h-2z"/>
      <path d="M20 10h-2a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2v-6a2 2 0 0 0-2-2h-2z"/>
    </svg>
  ),
  Microscope: ({ size = 20, color = 'currentColor' }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M6 18h12"/>
      <path d="M3 22h18"/>
      <path d="M14 6l4 4"/>
      <path d="M10 10l-4-4"/>
      <path d="M12 12a4 4 0 0 0 4-4c0-1-1-2-2-2s-2 1-2 2"/>
      <path d="M12 18v-6"/>
    </svg>
  ),
  // File & Upload
  File: ({ size = 20, color = 'currentColor' }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
      <line x1="16" y1="13" x2="8" y2="13"/>
      <line x1="16" y1="17" x2="8" y2="17"/>
      <polyline points="10 9 9 9 8 9"/>
    </svg>
  ),
  Upload: ({ size = 20, color = 'currentColor' }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
      <polyline points="17 8 12 3 7 8"/>
      <line x1="12" y1="3" x2="12" y2="15"/>
    </svg>
  ),
  Search: ({ size = 20, color = 'currentColor' }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8"/>
      <line x1="21" y1="21" x2="16.65" y2="16.65"/>
    </svg>
  ),
  // Actions
  Plus: ({ size = 20, color = 'currentColor' }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="5" x2="12" y2="19"/>
      <line x1="5" y1="12" x2="19" y2="12"/>
    </svg>
  ),
  ArrowRight: ({ size = 20, color = 'currentColor' }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="5" y1="12" x2="19" y2="12"/>
      <polyline points="12 5 19 12 12 19"/>
    </svg>
  ),
  ArrowLeft: ({ size = 20, color = 'currentColor' }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="19" y1="12" x2="5" y2="12"/>
      <polyline points="12 19 5 12 12 5"/>
    </svg>
  ),
  // Storage & Data
  Database: ({ size = 20, color = 'currentColor' }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <ellipse cx="12" cy="5" rx="9" ry="3"/>
      <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
      <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
    </svg>
  ),
  TrendingUp: ({ size = 20, color = 'currentColor' }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
      <polyline points="17 6 23 6 23 12"/>
    </svg>
  ),
  // User
  User: ({ size = 20, color = 'currentColor' }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
      <circle cx="12" cy="7" r="4"/>
    </svg>
  ),
}

// ==================== Design System ====================
const DesignTokens = {
  colors: {
    // 主色调 - 权威海军蓝，传达法律专业与信任
    primary: '#1e3a8a',
    primaryLight: '#1e40af',
    primaryDark: '#1e3a5f',
    // 强调色 - 信任金/琥珀色，用于关键行动点
    accent: '#b45309',
    accentLight: '#d97706',
    accentDark: '#92400e',
    // 背景色 - 柔和的灰白
    background: '#f8fafc',
    surface: '#ffffff',
    surfaceHover: '#f1f5f9',
    // 文字色 - 层次分明的灰度
    text: {
      primary: '#0f172a',
      secondary: '#475569',
      muted: '#94a3b8',
    },
    // 边框 - 柔和的灰色
    border: '#e2e8f0',
    // 状态色 - 协调的语义色系
    success: '#059669',
    successLight: '#d1fae5',
    warning: '#d97706',
    warningLight: '#fef3c7',
    error: '#dc2626',
    errorLight: '#fee2e2',
    info: '#2563eb',
    infoLight: '#dbeafe',
    // 图标背景色 - 柔和的色调
    iconBg: {
      blue: '#eff6ff',
      green: '#f0fdf4',
      amber: '#fffbeb',
      red: '#fef2f2',
      gray: '#f8fafc',
    }
  },
  fonts: {
    display: '"EB Garamond", Georgia, serif',
    body: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
    mono: '"JetBrains Mono", "Fira Code", monospace',
  },
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
    // 悬浮感阴影
    hover: '0 8px 16px -4px rgba(30, 58, 138, 0.15), 0 4px 8px -2px rgba(30, 58, 138, 0.1)',
    icon: '0 4px 8px -2px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    iconHover: '0 8px 16px -4px rgba(0, 0, 0, 0.15), 0 4px 8px -2px rgba(0, 0, 0, 0.1)',
    button: '0 4px 6px -1px rgba(30, 58, 138, 0.2), 0 2px 4px -1px rgba(30, 58, 138, 0.1)',
    buttonHover: '0 10px 20px -4px rgba(30, 58, 138, 0.3), 0 6px 8px -2px rgba(30, 58, 138, 0.15)',
  },
  radii: {
    sm: '6px',
    md: '10px',
    lg: '16px',
    xl: '24px',
    full: '9999px',
  },
}

// ==================== 通用组件 ====================
const Button = ({ children, variant = 'primary', size = 'md', disabled, onClick, style = {}, icon }) => {
  const [isHovered, setIsHovered] = React.useState(false)
  
  const baseStyles = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    borderRadius: DesignTokens.radii.md,
    fontWeight: 600,
    fontFamily: DesignTokens.fonts.body,
    cursor: disabled ? 'not-allowed' : 'pointer',
    transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
    opacity: disabled ? 0.5 : 1,
    border: 'none',
    outline: 'none',
    transform: isHovered && !disabled ? 'translateY(-2px)' : 'translateY(0)',
  }
  
  const variants = {
    primary: { 
      background: `linear-gradient(135deg, ${DesignTokens.colors.primary}, ${DesignTokens.colors.primaryLight})`,
      color: 'white',
      boxShadow: isHovered && !disabled ? DesignTokens.shadows.buttonHover : DesignTokens.shadows.button,
    },
    secondary: { 
      background: DesignTokens.colors.surface,
      color: DesignTokens.colors.text.primary,
      border: `1px solid ${DesignTokens.colors.border}`,
      boxShadow: isHovered && !disabled ? DesignTokens.shadows.md : DesignTokens.shadows.sm,
    },
    ghost: { 
      background: isHovered && !disabled ? DesignTokens.colors.surfaceHover : 'transparent', 
      color: DesignTokens.colors.text.secondary,
    },
    accent: {
      background: DesignTokens.colors.accent,
      color: 'white',
      boxShadow: isHovered && !disabled ? '0 10px 20px -4px rgba(180, 83, 9, 0.4), 0 6px 8px -2px rgba(180, 83, 9, 0.2)' : '0 4px 6px -1px rgba(180, 83, 9, 0.3), 0 2px 4px -1px rgba(180, 83, 9, 0.15)',
    },
  }
  
  const sizes = {
    sm: { padding: '8px 14px', fontSize: '13px' },
    md: { padding: '12px 20px', fontSize: '14px' },
    lg: { padding: '14px 28px', fontSize: '15px' },
  }
  
  return (
    <button 
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{ 
        ...baseStyles, 
        ...variants[variant], 
        ...sizes[size], 
        ...style,
        ':hover': !disabled ? {
          transform: 'translateY(-1px)',
          boxShadow: variant === 'primary' ? '0 4px 12px rgba(30, 58, 95, 0.4)' : DesignTokens.shadows.md,
        } : {},
      }}
      disabled={disabled}
      onClick={onClick}
    >
      {icon && <span>{icon}</span>}
      {children}
    </button>
  )
}

const Card = ({ children, style = {}, hover = false, onClick, padding = '24px' }) => {
  const [isHovered, setIsHovered] = React.useState(false)
  
  return (
    <div 
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        background: DesignTokens.colors.surface,
        borderRadius: DesignTokens.radii.lg,
        boxShadow: hover && isHovered ? DesignTokens.shadows.lg : DesignTokens.shadows.md,
        padding,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        cursor: onClick ? 'pointer' : undefined,
        border: `1px solid ${DesignTokens.colors.border}`,
        transform: hover && isHovered ? 'translateY(-4px)' : 'translateY(0)',
        ...style,
      }}
    >{children}</div>
  )
}

const Badge = ({ children, variant = 'blue', size = 'md' }) => {
  const colors = {
    blue: { bg: DesignTokens.colors.infoLight, color: '#1e40af', border: '#93c5fd' },
    green: { bg: DesignTokens.colors.successLight, color: '#065f46', border: '#6ee7b7' },
    yellow: { bg: DesignTokens.colors.warningLight, color: '#92400e', border: '#fcd34d' },
    red: { bg: DesignTokens.colors.errorLight, color: '#991b1b', border: '#fca5a5' },
    gray: { bg: '#f1f5f9', color: '#475569', border: '#cbd5e1' },
    purple: { bg: '#f3e8ff', color: '#7c3aed', border: '#c4b5fd' },
    accent: { bg: '#e0e7ff', color: DesignTokens.colors.accentDark, border: DesignTokens.colors.accent },
  }
  
  const sizes = {
    sm: { padding: '2px 8px', fontSize: '11px' },
    md: { padding: '4px 10px', fontSize: '12px' },
    lg: { padding: '6px 14px', fontSize: '13px' },
  }
  
  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      padding: sizes[size].padding,
      borderRadius: DesignTokens.radii.full,
      fontSize: sizes[size].fontSize,
      fontWeight: 600,
      fontFamily: DesignTokens.fonts.body,
      background: colors[variant].bg,
      color: colors[variant].color,
      border: `1px solid ${colors[variant].border}`,
    }}>{children}</span>
  )
}

// 带悬浮效果的图标容器
const IconBox = ({ children, bg, size = 56, hover = true }) => {
  const [isHovered, setIsHovered] = React.useState(false)
  
  return (
    <div
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        width: `${size}px`,
        height: `${size}px`,
        background: bg,
        borderRadius: size >= 56 ? DesignTokens.radii.lg : DesignTokens.radii.md,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: hover && isHovered ? DesignTokens.shadows.iconHover : DesignTokens.shadows.icon,
        transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
        transform: hover && isHovered ? 'translateY(-3px) scale(1.05)' : 'translateY(0) scale(1)',
      }}
    >
      {children}
    </div>
  )
}

const Modal = ({ isOpen, onClose, title, children, size = 'md' }) => {
  if (!isOpen) return null
  
  const sizes = {
    sm: { maxWidth: '400px' },
    md: { maxWidth: '560px' },
    lg: { maxWidth: '720px' },
    xl: { maxWidth: '960px' },
  }
  
  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(15, 31, 51, 0.6)',
      backdropFilter: 'blur(4px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '24px',
    }} onClick={onClose}>
      <div style={{
        background: DesignTokens.colors.surface,
        borderRadius: DesignTokens.radii.xl,
        width: '100%',
        maxHeight: '90vh',
        overflow: 'auto',
        boxShadow: DesignTokens.shadows.xl,
        border: `1px solid ${DesignTokens.colors.border}`,
        ...sizes[size],
      }} onClick={e => e.stopPropagation()}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '20px 24px',
          borderBottom: `1px solid ${DesignTokens.colors.border}`,
          background: `linear-gradient(135deg, ${DesignTokens.colors.primary}, ${DesignTokens.colors.primaryLight})`,
          color: 'white',
        }}>
          <h3 style={{ fontSize: '18px', fontWeight: 600, fontFamily: DesignTokens.fonts.display }}>{title}</h3>
          <button onClick={onClose} style={{
            background: 'rgba(255,255,255,0.2)',
            border: 'none',
            fontSize: '20px',
            color: 'white',
            cursor: 'pointer',
            width: '32px',
            height: '32px',
            borderRadius: DesignTokens.radii.full,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'background 0.2s',
          }}>×</button>
        </div>
        <div style={{ padding: '24px' }}>
          {children}
        </div>
      </div>
    </div>
  )
}

const ProgressBar = ({ progress, style = {}, size = 'md', variant = 'primary' }) => {
  const heights = { sm: '4px', md: '8px', lg: '12px' }
  const colors = {
    primary: `linear-gradient(90deg, ${DesignTokens.colors.accent}, ${DesignTokens.colors.accentLight})`,
    accent: `linear-gradient(90deg, ${DesignTokens.colors.accent}, ${DesignTokens.colors.accentLight})`,
    success: `linear-gradient(90deg, ${DesignTokens.colors.success}, #34d399)`,
  }
  
  return (
    <div style={{
      height: heights[size],
      background: DesignTokens.colors.border,
      borderRadius: DesignTokens.radii.full,
      overflow: 'hidden',
      ...style,
    }}>
      <div style={{
        height: '100%',
        background: colors[variant],
        borderRadius: DesignTokens.radii.full,
        transition: 'width 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
        width: `${progress}%`,
      }} />
    </div>
  )
}

const StatusBadge = ({ status }) => {
  const statusMap = {
    draft: { variant: 'gray', text: '草稿' },
    submitted: { variant: 'blue', text: '已提交' },
    queued: { variant: 'blue', text: '排队中' },
    parsing: { variant: 'yellow', text: '解析中' },
    extracting: { variant: 'yellow', text: '特征提取' },
    embedding: { variant: 'yellow', text: '向量化' },
    searching: { variant: 'yellow', text: '检索中' },
    reranking: { variant: 'yellow', text: '重排序' },
    reporting: { variant: 'yellow', text: '报告生成' },
    completed: { variant: 'green', text: '已完成' },
    partial: { variant: 'yellow', text: '部分完成' },
    failed: { variant: 'red', text: '失败' },
    cancelled: { variant: 'gray', text: '已取消' },
    timeout: { variant: 'red', text: '超时' },
    archived: { variant: 'purple', text: '已归档' },
  }
  
  const config = statusMap[status] || statusMap.draft
  
  return (
    <Badge variant={config.variant}>
      {config.text}
    </Badge>
  )
}

// ==================== Header ====================
const Header = () => {
  const navigate = useNavigate()
  const location = useLocation()
  
  const navItems = [
    { path: '/', label: '首页', Icon: Icons.Home },
    { path: '/tasks', label: '分析任务', Icon: Icons.Tasks },
    { path: '/libraries', label: '专利库', Icon: Icons.Library },
  ]
  
  return (
    <header style={{
      background: DesignTokens.colors.surface,
      borderBottom: `1px solid ${DesignTokens.colors.border}`,
      padding: '0 32px',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      boxShadow: DesignTokens.shadows.sm,
    }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '72px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
          <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '12px', textDecoration: 'none' }}>
            <div style={{
              width: 44,
              height: 44,
              background: `linear-gradient(135deg, ${DesignTokens.colors.primary}, ${DesignTokens.colors.primaryLight})`,
              borderRadius: DesignTokens.radii.md,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: '22px',
              fontWeight: 700,
              fontFamily: DesignTokens.fonts.display,
              boxShadow: '0 4px 12px rgba(30, 58, 95, 0.3)',
            }}>P</div>
            <div>
              <span style={{ fontSize: '20px', fontWeight: 700, color: DesignTokens.colors.primary, fontFamily: DesignTokens.fonts.display, letterSpacing: '-0.5px' }}>PatentAI</span>
              <span style={{ display: 'block', fontSize: '10px', color: DesignTokens.colors.text.muted, letterSpacing: '1px', textTransform: 'uppercase' }}>Intelligence Platform</span>
            </div>
          </Link>
          
          <nav style={{ display: 'flex', gap: '8px' }}>
            {navItems.map((item) => {
              const isActive = location.pathname === item.path || location.pathname.startsWith(item.path + '/')
              return (
                <Link 
                  key={item.path}
                  to={item.path} 
                  style={{ 
                    padding: '10px 16px', 
                    borderRadius: DesignTokens.radii.md, 
                    textDecoration: 'none', 
                    color: isActive ? DesignTokens.colors.primary : DesignTokens.colors.text.secondary, 
                    fontSize: '14px', 
                    fontWeight: isActive ? 600 : 500,
                    background: isActive ? DesignTokens.colors.iconBg.blue : 'transparent',
                    transition: 'all 0.2s',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                  }}
                >
                  <item.Icon size={18} color={isActive ? DesignTokens.colors.primary : DesignTokens.colors.text.secondary} />
                  {item.label}
                </Link>
              )
            })}
          </nav>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <Button onClick={() => navigate('/tasks/new')} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Icons.Plus size={18} color="white" />
            新建分析
          </Button>
          <div style={{
            width: 36,
            height: 36,
            background: DesignTokens.colors.primaryLight,
            borderRadius: DesignTokens.radii.full,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: 600,
            color: 'white',
            boxShadow: DesignTokens.shadows.sm,
          }}>张</div>
        </div>
      </div>
    </header>
  )
}

// ==================== 文件上传组件 ====================
const FileUploader = ({ onFileSelect, accept = ".pdf,.docx,.txt,.jpg,.jpeg,.png", maxSize = 50 }) => {
  const [dragActive, setDragActive] = useState(false)
  const inputRef = useRef(null)
  
  const handleDrag = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])
  
  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileSelect(Array.from(e.dataTransfer.files))
    }
  }, [onFileSelect])
  
  const handleChange = useCallback((e) => {
    e.preventDefault()
    if (e.target.files && e.target.files.length > 0) {
      onFileSelect(Array.from(e.target.files))
    }
  }, [onFileSelect])
  
  const onButtonClick = () => {
    inputRef.current?.click()
  }
  
  return (
    <div
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      onClick={onButtonClick}
      style={{
        padding: '56px 48px',
        border: `2px dashed ${dragActive ? DesignTokens.colors.primary : DesignTokens.colors.border}`,
        borderRadius: DesignTokens.radii.lg,
        background: dragActive ? 'rgba(30, 58, 95, 0.03)' : DesignTokens.colors.background,
        textAlign: 'center',
        cursor: 'pointer',
        transition: 'all 0.3s ease',
      }}
    >
      <input
        ref={inputRef}
        type="file"
        style={{ display: 'none' }}
        onChange={handleChange}
        accept={accept}
      />
      <div style={{ margin: '0 auto 24px' }}>
        <IconBox bg={DesignTokens.colors.iconBg.blue} size={80}>
          <Icons.Upload size={32} color={DesignTokens.colors.primary} />
        </IconBox>
      </div>
      <p style={{ fontSize: '18px', fontWeight: 600, color: DesignTokens.colors.text.primary, marginBottom: '8px', fontFamily: DesignTokens.fonts.display }}>
        拖放文件到此处 或 点击上传
      </p>
      <p style={{ fontSize: '14px', color: DesignTokens.colors.text.secondary, marginBottom: '4px' }}>
        支持 PDF、DOCX、TXT、图片格式
      </p>
      <p style={{ fontSize: '13px', color: DesignTokens.colors.text.muted }}>
        最大 {maxSize}MB
      </p>
    </div>
  )
}

// ==================== 专利库详情页面 ====================
const LibraryDetail = () => {
  const navigate = useNavigate()
  const { id } = useParams()
  const [library, setLibrary] = useState(null)
  const [patents, setPatents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  useEffect(() => {
    const fetchLibraryDetail = async () => {
      try {
        setLoading(true)
        const [libData, patentsData] = await Promise.all([
          api.libraries.get(id),
          api.patents.list(id)
        ])
        setLibrary(libData)
        setPatents(patentsData)
      } catch (err) {
        console.error('Failed to fetch library:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    if (id) {
      fetchLibraryDetail()
    }
  }, [id])
  
  if (loading) return <div style={{ padding: '40px', textAlign: 'center' }}>加载中...</div>
  if (error) return <div style={{ padding: '40px', textAlign: 'center', color: 'red' }}>加载失败: {error}</div>
  if (!library) return <div style={{ padding: '40px', textAlign: 'center' }}>库不存在</div>
  
  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '40px 32px' }}>
      <button 
        onClick={() => navigate('/libraries')} 
        style={{ 
          background: 'none', 
          border: 'none', 
          color: DesignTokens.colors.text.muted, 
          cursor: 'pointer', 
          marginBottom: '16px',
          fontSize: '14px',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
        }}
      >
        ← 返回专利库列表
      </button>
      
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '32px', fontWeight: 700, marginBottom: '10px', fontFamily: DesignTokens.fonts.display, color: DesignTokens.colors.primary }}>{library.name}</h1>
        <p style={{ fontSize: '15px', color: DesignTokens.colors.text.secondary }}>{library.description || '暂无描述'}</p>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '32px' }}>
        <Card style={{ textAlign: 'center', padding: '28px' }}>
          <div style={{ fontSize: '36px', fontWeight: 700, color: DesignTokens.colors.primary, fontFamily: DesignTokens.fonts.display }}>{patents.length}</div>
          <div style={{ fontSize: '14px', color: DesignTokens.colors.text.muted, marginTop: '8px' }}>专利总数</div>
        </Card>
        <Card style={{ textAlign: 'center', padding: '28px' }}>
          <div style={{ fontSize: '36px', fontWeight: 700, color: DesignTokens.colors.success, fontFamily: DesignTokens.fonts.display }}>{(library.size_mb || 0).toFixed(1)}</div>
          <div style={{ fontSize: '14px', color: DesignTokens.colors.text.muted, marginTop: '8px' }}>存储大小 (MB)</div>
        </Card>
        <Card style={{ textAlign: 'center', padding: '28px' }}>
          <div style={{ fontSize: '36px', fontWeight: 700, color: DesignTokens.colors.accent, fontFamily: DesignTokens.fonts.display }}>{new Date(library.created_at).toLocaleDateString()}</div>
          <div style={{ fontSize: '14px', color: DesignTokens.colors.text.muted, marginTop: '8px' }}>创建日期</div>
        </Card>
      </div>
      
      <Card>
        <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '20px', fontFamily: DesignTokens.fonts.display, color: DesignTokens.colors.text.primary }}>专利列表</h3>
        {patents.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: DesignTokens.colors.text.muted }}>
            暂无专利，请先导入专利
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {patents.map((patent) => (
              <div 
                key={patent.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '16px',
                  padding: '16px 20px',
                  background: DesignTokens.colors.background,
                  borderRadius: DesignTokens.radii.md,
                }}
              >
                <Icons.File size={20} color={DesignTokens.colors.text.muted} />
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: '15px', color: DesignTokens.colors.text.primary }}>{patent.title}</div>
                  <div style={{ fontSize: '13px', color: DesignTokens.colors.text.muted, marginTop: '4px' }}>
                    {patent.publication_no || patent.application_no || '无专利号'} · IPC: {patent.ipc || 'N/A'}
                  </div>
                </div>
                <Button variant="ghost" size="sm" onClick={() => api.patents.delete(patent.id).then(() => setPatents(patents.filter(p => p.id !== patent.id)))}>
                  删除
                </Button>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}

// ==================== 专利库管理页面 ====================
const LibraryManagement = () => {
  const navigate = useNavigate()
  const [libraries, setLibraries] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [selectedLibrary, setSelectedLibrary] = useState(null)
  const [newLibraryName, setNewLibraryName] = useState('')
  const [newLibraryDesc, setNewLibraryDesc] = useState('')
  
  // Fetch libraries from API
  useEffect(() => {
    fetchLibraries()
  }, [])
  
  const fetchLibraries = async () => {
    try {
      setLoading(true)
      const data = await api.libraries.list()
      setLibraries(data)
    } catch (error) {
      console.error('Failed to fetch libraries:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const handleCreateLibrary = async () => {
    if (!newLibraryName.trim()) return
    try {
      await api.libraries.create({
        name: newLibraryName,
        description: newLibraryDesc,
      })
      setNewLibraryName('')
      setNewLibraryDesc('')
      setShowCreateModal(false)
      await fetchLibraries()
    } catch (error) {
      console.error('Failed to create library:', error)
      alert('创建失败: ' + error.message)
    }
  }
  
  const handlePatentUpload = async (libraryId, files) => {
    console.log('Upload completed for library', libraryId, 'files:', files)
    if (files.length > 0) {
      alert(`成功导入 ${files.length} 个文件`)
    }
    setShowUploadModal(false)
    await fetchLibraries()
  }
  
  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '40px 32px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '40px' }}>
        <div>
          <h1 style={{ fontSize: '32px', fontWeight: 700, marginBottom: '8px', fontFamily: DesignTokens.fonts.display, color: DesignTokens.colors.primary }}>专利库管理</h1>
          <p style={{ fontSize: '15px', color: DesignTokens.colors.text.secondary }}>管理您的专利比对库，支持批量导入和自动分类</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Icons.Plus size={18} color="white" />
          创建新库
        </Button>
      </div>
      
      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '40px' }}>
        {[
          { label: '专利库总数', value: libraries.length, Icon: Icons.Library, bg: DesignTokens.colors.iconBg.blue, color: DesignTokens.colors.primary },
          { label: '专利总数', value: libraries.reduce((sum, l) => sum + (l.patent_count || 0), 0).toLocaleString(), Icon: Icons.File, bg: DesignTokens.colors.iconBg.green, color: DesignTokens.colors.success },
          { label: '存储空间', value: (libraries.reduce((sum, l) => sum + (l.size_mb || 0), 0) / 1024).toFixed(1) + 'GB', Icon: Icons.Database, bg: DesignTokens.colors.iconBg.amber, color: DesignTokens.colors.warning },
        ].map((stat, i) => (
          <Card key={i} hover style={{ textAlign: 'center', padding: '28px' }}>
            <div style={{ margin: '0 auto 16px' }}>
              <IconBox bg={stat.bg} size={52}>
                <stat.Icon size={26} color={stat.color} />
              </IconBox>
            </div>
            <div style={{ fontSize: '32px', fontWeight: 700, color: DesignTokens.colors.text.primary, fontFamily: DesignTokens.fonts.display }}>{stat.value}</div>
            <div style={{ fontSize: '14px', color: DesignTokens.colors.text.muted, marginTop: '4px' }}>{stat.label}</div>
          </Card>
        ))}
      </div>
      
      {/* Libraries Grid */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: DesignTokens.colors.text.muted }}>加载中...</div>
      ) : libraries.length === 0 ? (
        <Card style={{ padding: '60px', textAlign: 'center' }}>
          <p style={{ color: DesignTokens.colors.text.muted, marginBottom: '20px' }}>暂无专利库，创建您的第一个专利库</p>
          <Button onClick={() => setShowCreateModal(true)}>
            <Icons.Plus size={18} color="white" />
            创建新库
          </Button>
        </Card>
      ) : (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px' }}>
        {libraries.map((lib) => (
          <Card key={lib.id} hover style={{ position: 'relative', padding: '28px' }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '16px', marginBottom: '24px' }}>
              <IconBox bg={DesignTokens.colors.iconBg.blue} size={56}>
                <Icons.Library size={28} color={DesignTokens.colors.primary} />
              </IconBox>
              <div style={{ flex: 1 }}>
                <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '4px', color: DesignTokens.colors.text.primary }}>{lib.name}</h3>
                <p style={{ fontSize: '13px', color: DesignTokens.colors.text.muted }}>
                  {new Date(lib.updated_at).toLocaleDateString('zh-CN')} 更新
                </p>
              </div>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
              <div style={{ padding: '12px', background: DesignTokens.colors.background, borderRadius: DesignTokens.radii.md }}>
                <div style={{ fontSize: '24px', fontWeight: 700, color: DesignTokens.colors.primary, fontFamily: DesignTokens.fonts.display }}>{lib.patent_count || 0}</div>
                <div style={{ fontSize: '13px', color: DesignTokens.colors.text.muted }}>份专利</div>
              </div>
              <div style={{ padding: '12px', background: DesignTokens.colors.background, borderRadius: DesignTokens.radii.md }}>
                <div style={{ fontSize: '24px', fontWeight: 700, color: DesignTokens.colors.text.primary, fontFamily: DesignTokens.fonts.display }}>
                  {((lib.size_mb || 0) / 1024).toFixed(1)}GB
                </div>
                <div style={{ fontSize: '13px', color: DesignTokens.colors.text.muted }}>存储空间</div>
              </div>
            </div>
            
            {lib.description && (
              <p style={{ fontSize: '14px', color: DesignTokens.colors.text.secondary, marginBottom: '20px', lineHeight: 1.6 }}>
                {lib.description}
              </p>
            )}
            
            <div style={{ display: 'flex', gap: '10px' }}>
              <Button 
                variant="secondary" 
                size="sm" 
                style={{ flex: 1 }}
                onClick={() => navigate(`/libraries/${lib.id}`)}
              >
                查看详情
              </Button>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={(e) => {
                  e.stopPropagation()
                  setSelectedLibrary(lib)
                  setShowUploadModal(true)
                }}
              >
                导入专利
              </Button>
            </div>
          </Card>
        ))}
      </div>
      )}
      
      {/* Create Library Modal */}
      <Modal 
        isOpen={showCreateModal} 
        onClose={() => setShowCreateModal(false)}
        title="创建新专利库"
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '8px', color: DesignTokens.colors.text.primary }}>
              库名称 *
            </label>
            <input
              type="text"
              value={newLibraryName}
              onChange={(e) => setNewLibraryName(e.target.value)}
              placeholder="例如：移动端视频编辑库"
              style={{
                width: '100%',
                padding: '12px 16px',
                border: `1px solid ${DesignTokens.colors.border}`,
                borderRadius: DesignTokens.radii.md,
                fontSize: '14px',
                fontFamily: DesignTokens.fonts.body,
                transition: 'border-color 0.2s',
                outline: 'none',
              }}
            />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '8px', color: DesignTokens.colors.text.primary }}>
              描述
            </label>
            <textarea
              value={newLibraryDesc}
              onChange={(e) => setNewLibraryDesc(e.target.value)}
              placeholder="描述这个专利库的用途和范围..."
              rows={3}
              style={{
                width: '100%',
                padding: '12px 16px',
                border: `1px solid ${DesignTokens.colors.border}`,
                borderRadius: DesignTokens.radii.md,
                fontSize: '14px',
                fontFamily: DesignTokens.fonts.body,
                resize: 'vertical',
                outline: 'none',
              }}
            />
          </div>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '8px' }}>
            <Button variant="secondary" onClick={() => setShowCreateModal(false)}>
              取消
            </Button>
            <Button onClick={handleCreateLibrary} disabled={!newLibraryName.trim()}>
              创建
            </Button>
          </div>
        </div>
      </Modal>
      
      {/* Upload Patents Modal */}
      <Modal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        title={`导入专利到「${selectedLibrary?.name}」`}
        size="lg"
      >
        <LibraryPatentUpload 
          library={selectedLibrary}
          onUpload={(files) => handlePatentUpload(selectedLibrary?.id, files)}
          onClose={() => setShowUploadModal(false)}
        />
      </Modal>
    </div>
  )
}

// ==================== 专利库批量上传组件 ====================
const LibraryPatentUpload = ({ library, onUpload, onClose }) => {
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [isUploading, setIsUploading] = useState(false)
  
  const handleFileSelect = (files) => {
    const newFiles = Array.from(files).map(file => ({
      id: Date.now() + Math.random(),
      file,
      name: file.name,
      size: (file.size / 1024 / 1024).toFixed(2),
      status: 'pending',
      progress: 0,
    }))
    setUploadedFiles([...uploadedFiles, ...newFiles])
  }
  
  const startUpload = async () => {
    setIsUploading(true)
    const pendingFiles = uploadedFiles.filter(f => f.status === 'pending')
    let successCount = 0
    let errorCount = 0
    
    for (let file of pendingFiles) {
      setUploadedFiles(prev => prev.map(f => 
        f.id === file.id ? { ...f, status: 'uploading', progress: 10 } : f
      ))
      
      try {
        console.log('Uploading file:', file.name)
        
        // Step 1: Upload file
        setUploadedFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, progress: 30 } : f
        ))
        const uploadResult = await api.upload.file(file.file)
        console.log('Upload result:', uploadResult)
        const fileId = uploadResult.file_id
        
        // Step 2: Parse file
        setUploadedFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, progress: 60 } : f
        ))
        const parseResult = await api.upload.parse(fileId)
        console.log('Parse result:', parseResult)
        
        // Step 3: Save to library
        setUploadedFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, progress: 90 } : f
        ))
        const saveResult = await api.upload.save({
          file_id: fileId,
          library_id: library.id,
          patent_info: parseResult.patent_info,
          quality_score: parseResult.quality_score,
        })
        console.log('Save result:', saveResult)
        
        setUploadedFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, status: 'completed', progress: 100 } : f
        ))
        successCount++
      } catch (error) {
        console.error('Upload failed for', file.name, ':', error)
        errorCount++
        setUploadedFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, status: 'error', error: error.message || '上传失败' } : f
        ))
      }
    }
    
    setIsUploading(false)
    console.log('Upload finished. Success:', successCount, 'Errors:', errorCount)
  }
  
  const removeFile = (id) => {
    setUploadedFiles(uploadedFiles.filter(f => f.id !== id))
  }
  
  const completedCount = uploadedFiles.filter(f => f.status === 'completed').length
  
  return (
    <div>
      {uploadedFiles.length === 0 && (
        <FileUploader 
          onFileSelect={handleFileSelect}
          maxSize={100}
        />
      )}
      
      {uploadedFiles.length > 0 && (
        <div style={{ marginBottom: '24px' }}>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            marginBottom: '16px',
            padding: '16px 20px',
            background: DesignTokens.colors.background,
            borderRadius: DesignTokens.radii.md,
          }}>
            <span style={{ fontSize: '15px', fontWeight: 600, color: DesignTokens.colors.text.primary }}>
              已选择 {uploadedFiles.length} 个文件
            </span>
            {completedCount > 0 && (
              <Badge variant="green">{completedCount} 个已完成</Badge>
            )}
          </div>
          
          <div style={{ 
            maxHeight: '320px', 
            overflow: 'auto',
            border: `1px solid ${DesignTokens.colors.border}`,
            borderRadius: DesignTokens.radii.md,
          }}>
            {uploadedFiles.map((file) => (
              <div 
                key={file.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '14px',
                  padding: '14px 18px',
                  borderBottom: `1px solid ${DesignTokens.colors.border}`,
                  background: file.status === 'completed' ? `${DesignTokens.colors.success}08` : 'white',
                }}
              >
                <Icons.File size={20} color={DesignTokens.colors.text.muted} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: '14px', fontWeight: 500, color: DesignTokens.colors.text.primary }}>{file.name}</div>
                  <div style={{ fontSize: '12px', color: DesignTokens.colors.text.muted, marginTop: '2px' }}>
                    {file.size} MB
                    {file.status === 'error' && file.error && (
                      <span style={{ color: DesignTokens.colors.error, marginLeft: '8px' }}>错误: {file.error}</span>
                    )}
                  </div>
                  {file.status === 'uploading' && (
                    <div style={{ marginTop: '8px' }}>
                      <ProgressBar progress={file.progress} size="sm" />
                    </div>
                  )}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  {file.status === 'completed' && (
                    <Icons.Check size={20} color={DesignTokens.colors.success} />
                  )}
                  {file.status === 'error' && (
                    <Icons.AlertTriangle size={20} color={DesignTokens.colors.error} />
                  )}
                  {!isUploading && (
                    <button
                      onClick={() => removeFile(file.id)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: DesignTokens.colors.text.muted,
                        cursor: 'pointer',
                        fontSize: '20px',
                        padding: '4px',
                      }}
                    >
                      ×
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
          
          {!isUploading && completedCount < uploadedFiles.length && (
            <div style={{ marginTop: '16px' }}>
              <Button variant="secondary" size="sm" onClick={() => document.getElementById('additional-files').click()}>
                + 添加更多文件
              </Button>
              <input
                id="additional-files"
                type="file"
                multiple
                style={{ display: 'none' }}
                onChange={(e) => handleFileSelect(e.target.files)}
                accept=".pdf,.docx,.txt,.jpg,.jpeg,.png"
              />
            </div>
          )}
        </div>
      )}
      
      <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
        <Button variant="secondary" onClick={onClose}>
          取消
        </Button>
        {uploadedFiles.length > 0 && completedCount < uploadedFiles.length && (
          <Button onClick={startUpload} disabled={isUploading}>
            {isUploading ? '上传中...' : `开始导入 (${uploadedFiles.length}个文件)`}
          </Button>
        )}
        {completedCount === uploadedFiles.length && uploadedFiles.length > 0 && (
          <Button onClick={() => {
            const completedFiles = uploadedFiles.filter(f => f.status === 'completed')
            onUpload(completedFiles)
          }}>
            完成 ({completedCount}个文件已导入)
          </Button>
        )}
      </div>
    </div>
  )
}

// ==================== 首页 ====================
const Dashboard = () => {
  const navigate = useNavigate()
  const [stats, setStats] = useState({
    total: 0,
    running: 0,
    completed: 0,
    failed: 0,
  })
  const [recentTasks, setRecentTasks] = useState([])
  const [libraries, setLibraries] = useState([])
  const [loading, setLoading] = useState(true)
  
  // Fetch real data from API
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        
        // Fetch tasks
        const tasksData = await api.tasks.list()
        const tasks = tasksData.items || []
        
        // Calculate stats
        const running = tasks.filter(t => ['queued', 'running', 'parsing', 'extracting', 'embedding', 'searching'].includes(t.status)).length
        const completed = tasks.filter(t => t.status === 'completed').length
        const failed = tasks.filter(t => t.status === 'failed').length
        
        setStats({
          total: tasks.length,
          running,
          completed,
          failed,
        })
        
        // Get recent tasks (last 5)
        const sorted = tasks.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 5)
        setRecentTasks(sorted)
        
        // Fetch libraries count
        const libsData = await api.libraries.list()
        setLibraries(libsData)
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }
    
    fetchData()
    // Refresh every 10 seconds
    const interval = setInterval(fetchData, 10000)
    return () => clearInterval(interval)
  }, [])
  
  const templates = [
    { Icon: Icons.Target, title: '侵权分析', desc: '发现潜在侵权风险', bg: DesignTokens.colors.iconBg.red, color: DesignTokens.colors.error },
    { Icon: Icons.Lightbulb, title: '创新挖掘', desc: '识别技术空白点', bg: DesignTokens.colors.iconBg.amber, color: DesignTokens.colors.warning },
    { Icon: Icons.Binoculars, title: '竞争监控', desc: '追踪竞争对手动态', bg: DesignTokens.colors.iconBg.blue, color: DesignTokens.colors.primary },
    { Icon: Icons.Microscope, title: '技术调研', desc: '分析技术发展趋势', bg: DesignTokens.colors.iconBg.green, color: DesignTokens.colors.success },
  ]
  
  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '40px 32px' }}>
      {/* Welcome Section */}
      <div style={{ marginBottom: '48px' }}>
        <h1 style={{ 
          fontSize: '36px', 
          fontWeight: 700, 
          marginBottom: '12px', 
          fontFamily: DesignTokens.fonts.display,
          color: DesignTokens.colors.primary,
        }}>
          欢迎回来，张律师
        </h1>
        <p style={{ fontSize: '16px', color: DesignTokens.colors.text.secondary }}>
          今天有什么专利分析任务需要处理？
        </p>
      </div>
      
      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '48px' }}>
        {[
          { label: '全部任务', value: stats.total, Icon: Icons.Chart, bg: DesignTokens.colors.iconBg.blue, color: DesignTokens.colors.primary },
          { label: '进行中', value: stats.running, Icon: Icons.Refresh, bg: DesignTokens.colors.iconBg.amber, color: DesignTokens.colors.warning },
          { label: '已完成', value: stats.completed, Icon: Icons.Check, bg: DesignTokens.colors.iconBg.green, color: DesignTokens.colors.success },
          { label: '失败', value: stats.failed, Icon: Icons.Alert, bg: DesignTokens.colors.iconBg.red, color: DesignTokens.colors.error },
        ].map((stat, i) => (
          <Card key={i} hover onClick={() => navigate('/tasks')} style={{ cursor: 'pointer' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <IconBox bg={stat.bg} size={52}>
                <stat.Icon size={24} color={stat.color} />
              </IconBox>
              <div>
                <div style={{ fontSize: '28px', fontWeight: 700, color: DesignTokens.colors.text.primary, fontFamily: DesignTokens.fonts.display }}>{stat.value}</div>
                <div style={{ fontSize: '13px', color: DesignTokens.colors.text.muted, marginTop: '2px' }}>{stat.label}</div>
              </div>
            </div>
          </Card>
        ))}
      </div>
      
      {/* Quick Start */}
      <div style={{ marginBottom: '48px' }}>
        <h2 style={{ fontSize: '20px', fontWeight: 600, marginBottom: '20px', fontFamily: DesignTokens.fonts.display, color: DesignTokens.colors.text.primary }}>快速开始</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px' }}>
          {templates.map((tpl, i) => (
            <Card 
              key={i} 
              hover 
              style={{ 
                padding: '28px', 
                textAlign: 'center',
                background: DesignTokens.colors.surface,
                border: `1px solid ${DesignTokens.colors.border}`,
                cursor: 'pointer',
              }}
              onClick={() => navigate('/tasks/new', { state: { template: tpl.title } })}
            >
              <div style={{ margin: '0 auto 16px' }}>
                <IconBox bg={tpl.bg} size={56}>
                  <tpl.Icon size={28} color={tpl.color} />
                </IconBox>
              </div>
              <div style={{ fontWeight: 600, color: DesignTokens.colors.text.primary, marginBottom: '6px', fontSize: '16px' }}>{tpl.title}</div>
              <div style={{ fontSize: '14px', color: DesignTokens.colors.text.muted }}>{tpl.desc}</div>
            </Card>
          ))}
        </div>
      </div>
      
      {/* Recent Tasks */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: 600, fontFamily: DesignTokens.fonts.display, color: DesignTokens.colors.text.primary }}>最近任务</h2>
          <Button variant="ghost" size="sm" onClick={() => navigate('/tasks')}>
            查看全部 →
          </Button>
        </div>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: DesignTokens.colors.text.muted }}>加载中...</div>
        ) : recentTasks.length === 0 ? (
          <Card style={{ padding: '40px', textAlign: 'center' }}>
            <p style={{ color: DesignTokens.colors.text.muted }}>暂无任务，点击"新建分析"开始</p>
          </Card>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {recentTasks.map((task) => (
              <Card 
                key={task.id} 
                hover 
                style={{ padding: '20px 24px', cursor: 'pointer' }}
                onClick={() => navigate(`/tasks/${task.id}`)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                  <StatusBadge status={task.status} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, color: DesignTokens.colors.text.primary, fontSize: '15px' }}>{task.name}</div>
                    <div style={{ fontSize: '13px', color: DesignTokens.colors.text.muted, marginTop: '4px' }}>
                      ID: {task.id.substring(0, 8)}... · {new Date(task.created_at).toLocaleString('zh-CN', { hour12: false })}
                    </div>
                  </div>
                  {task.status === 'completed' ? (
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '14px', color: DesignTokens.colors.success }}>已完成</div>
                    </div>
                  ) : (
                    <div style={{ width: '140px' }}>
                      <ProgressBar progress={task.progress} size="sm" />
                      <div style={{ fontSize: '12px', color: DesignTokens.colors.text.muted, marginTop: '6px', textAlign: 'right' }}>
                        {task.progress}%
                      </div>
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

// ==================== 任务列表页 ====================
const TaskList = () => {
  const navigate = useNavigate()
  const [filter, setFilter] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedTasks, setSelectedTasks] = useState([])
  const [showBatchActions, setShowBatchActions] = useState(false)
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  
  // Fetch tasks from API
  useEffect(() => {
    fetchTasks()
    // Refresh every 5 seconds
    const interval = setInterval(fetchTasks, 5000)
    return () => clearInterval(interval)
  }, [filter, searchQuery])
  
  const fetchTasks = async () => {
    try {
      setLoading(true)
      const params = {}
      if (filter !== 'all') params.status = filter
      if (searchQuery) params.search = searchQuery
      
      const data = await api.tasks.list(params)
      setTasks(data.items || [])
    } catch (error) {
      console.error('Failed to fetch tasks:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const handleDeleteTask = async (id) => {
    if (!confirm('确定要删除这个任务吗？')) return
    try {
      await api.tasks.delete(id)
      await fetchTasks()
    } catch (error) {
      console.error('Failed to delete task:', error)
      alert('删除失败: ' + error.message)
    }
  }
  
  // Calculate counts from real data
  const counts = {
    all: tasks.length,
    running: tasks.filter(t => ['queued', 'running', 'parsing', 'extracting', 'embedding', 'searching'].includes(t.status)).length,
    completed: tasks.filter(t => t.status === 'completed').length,
    failed: tasks.filter(t => ['failed', 'timeout'].includes(t.status)).length,
    draft: tasks.filter(t => t.status === 'draft').length,
  }
  
  const filterTasks = () => {
    let filtered = tasks
    if (filter !== 'all') {
      filtered = tasks.filter(t => {
        if (filter === 'running') return ['queued', 'running', 'parsing', 'extracting', 'embedding', 'searching'].includes(t.status)
        if (filter === 'completed') return t.status === 'completed'
        if (filter === 'failed') return ['failed', 'timeout'].includes(t.status)
        if (filter === 'draft') return t.status === 'draft'
        return true
      })
    }
    if (searchQuery) {
      filtered = filtered.filter(t => 
        t.name.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }
    return filtered
  }
  
  const filteredTasks = filterTasks()
  
  const toggleTaskSelection = (taskId) => {
    const newSelection = selectedTasks.includes(taskId)
      ? selectedTasks.filter(id => id !== taskId)
      : [...selectedTasks, taskId]
    setSelectedTasks(newSelection)
    setShowBatchActions(newSelection.length > 0)
  }
  
  const selectAll = () => {
    const allIds = filteredTasks.map(t => t.id)
    setSelectedTasks(allIds)
    setShowBatchActions(allIds.length > 0)
  }
  
  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '40px 32px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '32px' }}>
        <div>
          <h1 style={{ fontSize: '32px', fontWeight: 700, marginBottom: '8px', fontFamily: DesignTokens.fonts.display, color: DesignTokens.colors.primary }}>分析任务</h1>
          <p style={{ fontSize: '15px', color: DesignTokens.colors.text.secondary }}>管理您的专利相似度分析任务，查看执行状态和结果</p>
        </div>
        <Button onClick={() => navigate('/tasks/new')} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Icons.Plus size={18} color="white" />
          新建分析
        </Button>
      </div>
      
      <Card style={{ padding: '20px 24px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: '280px', position: 'relative' }}>
            <div style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)' }}>
              <Icons.Search size={18} color={DesignTokens.colors.text.muted} />
            </div>
            <input
              type="text"
              placeholder="搜索任务名称、专利号..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                padding: '12px 16px 12px 42px',
                border: `1px solid ${DesignTokens.colors.border}`,
                borderRadius: DesignTokens.radii.md,
                fontSize: '14px',
                fontFamily: DesignTokens.fonts.body,
                outline: 'none',
              }}
            />
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            {[
              { key: 'all', label: '全部', count: counts.all },
              { key: 'running', label: '进行中', count: counts.running },
              { key: 'completed', label: '已完成', count: counts.completed },
              { key: 'failed', label: '失败', count: counts.failed },
              { key: 'draft', label: '草稿', count: counts.draft },
            ].map((f) => (
              <button
                key={f.key}
                onClick={() => setFilter(f.key)}
                style={{
                  padding: '10px 18px',
                  borderRadius: DesignTokens.radii.full,
                  border: 'none',
                  background: filter === f.key ? DesignTokens.colors.primary : DesignTokens.colors.background,
                  color: filter === f.key ? 'white' : DesignTokens.colors.text.secondary,
                  fontSize: '14px',
                  fontWeight: filter === f.key ? 600 : 500,
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                }}
              >
                {f.label} ({f.count})
              </button>
            ))}
          </div>
        </div>
      </Card>
      
      {showBatchActions && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          padding: '16px 20px',
          background: DesignTokens.colors.background,
          borderRadius: DesignTokens.radii.md,
          marginBottom: '20px',
          border: `1px solid ${DesignTokens.colors.border}`,
        }}>
          <span style={{ fontSize: '15px', fontWeight: 600, color: DesignTokens.colors.text.primary }}>
            已选择 {selectedTasks.length} 个任务
          </span>
          <div style={{ display: 'flex', gap: '10px', marginLeft: 'auto' }}>
            <Button variant="secondary" size="sm">批量取消</Button>
            <Button variant="secondary" size="sm">批量归档</Button>
            <Button variant="ghost" size="sm" style={{ color: DesignTokens.colors.error }}>批量删除</Button>
          </div>
        </div>
      )}
      
      {loading ? (
        <Card style={{ padding: '60px', textAlign: 'center' }}>
          <p style={{ color: DesignTokens.colors.text.muted }}>加载中...</p>
        </Card>
      ) : filteredTasks.length === 0 ? (
        <Card style={{ padding: '60px', textAlign: 'center' }}>
          <p style={{ color: DesignTokens.colors.text.muted }}>暂无任务，点击"新建分析"开始</p>
        </Card>
      ) : (
      <Card style={{ padding: 0, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead style={{ background: DesignTokens.colors.background }}>
            <tr>
              <th style={{ padding: '16px 20px', textAlign: 'left', width: '44px' }}>
                <input 
                  type="checkbox" 
                  onChange={selectAll}
                  checked={selectedTasks.length === filteredTasks.length && filteredTasks.length > 0}
                  style={{ width: '18px', height: '18px' }}
                />
              </th>
              <th style={{ padding: '16px 20px', textAlign: 'left', fontSize: '13px', fontWeight: 600, color: DesignTokens.colors.text.secondary, textTransform: 'uppercase', letterSpacing: '0.5px' }}>任务名称</th>
              <th style={{ padding: '16px 20px', textAlign: 'left', fontSize: '13px', fontWeight: 600, color: DesignTokens.colors.text.secondary, textTransform: 'uppercase', letterSpacing: '0.5px' }}>目标专利</th>
              <th style={{ padding: '16px 20px', textAlign: 'left', fontSize: '13px', fontWeight: 600, color: DesignTokens.colors.text.secondary, textTransform: 'uppercase', letterSpacing: '0.5px' }}>状态</th>
              <th style={{ padding: '16px 20px', textAlign: 'left', fontSize: '13px', fontWeight: 600, color: DesignTokens.colors.text.secondary, textTransform: 'uppercase', letterSpacing: '0.5px' }}>进度</th>
              <th style={{ padding: '16px 20px', textAlign: 'left', fontSize: '13px', fontWeight: 600, color: DesignTokens.colors.text.secondary, textTransform: 'uppercase', letterSpacing: '0.5px' }}>创建者</th>
              <th style={{ padding: '16px 20px', textAlign: 'left', fontSize: '13px', fontWeight: 600, color: DesignTokens.colors.text.secondary, textTransform: 'uppercase', letterSpacing: '0.5px' }}>时间</th>
              <th style={{ padding: '16px 20px', textAlign: 'left', fontSize: '13px', fontWeight: 600, color: DesignTokens.colors.text.secondary, textTransform: 'uppercase', letterSpacing: '0.5px' }}>操作</th>
            </tr>
          </thead>
          <tbody>
            {filteredTasks.map((task) => (
              <tr key={task.id} style={{ borderTop: `1px solid ${DesignTokens.colors.border}`, transition: 'background 0.2s', ':hover': { background: DesignTokens.colors.background } }}>
                <td style={{ padding: '18px 20px' }}>
                  <input 
                    type="checkbox" 
                    checked={selectedTasks.includes(task.id)}
                    onChange={() => toggleTaskSelection(task.id)}
                    style={{ width: '18px', height: '18px' }}
                  />
                </td>
                <td style={{ padding: '18px 20px' }}>
                  <div style={{ fontWeight: 600, color: DesignTokens.colors.text.primary, fontSize: '14px' }}>{task.name}</div>
                  <div style={{ fontSize: '12px', color: DesignTokens.colors.text.muted, marginTop: '2px' }}>ID: {task.id.substring(0, 8)}...</div>
                </td>
                <td style={{ padding: '18px 20px', fontSize: '14px', color: DesignTokens.colors.text.secondary }}>
                  {task.target_patent?.title || '-'}
                </td>
                <td style={{ padding: '18px 20px' }}>
                  <StatusBadge status={task.status} />
                </td>
                <td style={{ padding: '18px 20px' }}>
                  {task.status === 'completed' ? (
                    <span style={{ fontWeight: 700, color: DesignTokens.colors.success, fontSize: '16px', fontFamily: DesignTokens.fonts.display }}>完成</span>
                  ) : task.progress > 0 ? (
                    <div style={{ width: '110px' }}>
                      <ProgressBar progress={task.progress} size="sm" />
                    </div>
                  ) : (
                    <span style={{ fontSize: '13px', color: DesignTokens.colors.text.muted }}>-</span>
                  )}
                </td>
                <td style={{ padding: '18px 20px', fontSize: '14px', color: DesignTokens.colors.text.secondary }}>
                  {task.owner_id || '系统'}
                </td>
                <td style={{ padding: '18px 20px', fontSize: '14px', color: DesignTokens.colors.text.muted }}>
                  {new Date(task.created_at).toLocaleString('zh-CN')}
                </td>
                <td style={{ padding: '18px 20px' }}>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <Button variant="ghost" size="sm" onClick={() => navigate(`/tasks/${task.id}`)}>
                      查看
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => handleDeleteTask(task.id)}>删除</Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
      )}
    </div>
  )
}

// ==================== 任务详情页 ====================
const TaskDetail = () => {
  const navigate = useNavigate()
  const { id } = useParams()
  const [activeTab, setActiveTab] = useState('overview')
  const [showCancelModal, setShowCancelModal] = useState(false)
  const [task, setTask] = useState(null)
  const [libraries, setLibraries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  useEffect(() => {
    const fetchTask = async () => {
      try {
        setLoading(true)
        console.log('Fetching task:', id)
        const [taskData, libsData] = await Promise.all([
          api.tasks.get(id),
          api.libraries.list()
        ])
        console.log('Task data:', taskData)
        console.log('Libraries:', libsData)
        setTask(taskData)
        setLibraries(libsData)
      } catch (err) {
        console.error('Failed to fetch task:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    if (id) {
      fetchTask()
    }
  }, [id])
  
  // Get library name from libraries list if library_name is null
  const getLibraryName = () => {
    if (task?.library_name) return task.library_name
    if (task?.library_id && libraries.length > 0) {
      const lib = libraries.find(l => l.id === task.library_id)
      return lib?.name || '未知库'
    }
    return '未知库'
  }
  
  const tabs = [
    { key: 'overview', label: '概览' },
    { key: 'stages', label: '执行详情' },
    { key: 'logs', label: '日志' },
    { key: 'config', label: '配置' },
  ]
  
  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '40px 32px' }}>
      <div style={{ marginBottom: '32px' }}>
        <button 
          onClick={() => navigate('/tasks')} 
          style={{ 
            background: 'none', 
            border: 'none', 
            color: DesignTokens.colors.text.muted, 
            cursor: 'pointer', 
            marginBottom: '16px',
            fontSize: '14px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
          }}
        >
          ← 返回任务列表
        </button>
        
        {loading && <div style={{ textAlign: 'center', padding: '60px' }}>加载中...</div>}
        {error && <div style={{ textAlign: 'center', padding: '60px', color: DesignTokens.colors.error }}>加载失败: {error}</div>}
        {!loading && !error && task && (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h1 style={{ fontSize: '32px', fontWeight: 700, marginBottom: '10px', fontFamily: DesignTokens.fonts.display, color: DesignTokens.colors.primary }}>{task.name}</h1>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <StatusBadge status={task.status} />
              <span style={{ fontSize: '14px', color: DesignTokens.colors.text.muted }}>
                进度: {task.progress}% · 创建于: {new Date(task.created_at).toLocaleString('zh-CN', { hour12: false })}
              </span>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            {task.status === 'completed' && (
              <>
                <Button variant="secondary" size="sm">查看结果</Button>
                <Button variant="secondary" size="sm">重新分析</Button>
                <Button variant="secondary" size="sm">克隆任务</Button>
                <Button variant="accent" size="sm">导出报告</Button>
              </>
            )}
            {['parsing', 'extracting', 'embedding', 'searching', 'reranking', 'reporting'].includes(task.status) && (
              <Button variant="ghost" size="sm" onClick={() => setShowCancelModal(true)} style={{ color: DesignTokens.colors.error }}>
                取消任务
              </Button>
            )}
            {task.status === 'failed' && (
              <>
                <Button variant="secondary" size="sm">重试</Button>
                <Button variant="ghost" size="sm">克隆</Button>
              </>
            )}
          </div>
        </div>
      )}
      </div>
      
      <div style={{ display: 'flex', gap: '4px', marginBottom: '28px', borderBottom: `1px solid ${DesignTokens.colors.border}` }}>
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            style={{
              padding: '14px 24px',
              border: 'none',
              background: 'none',
              fontSize: '15px',
              fontWeight: activeTab === tab.key ? 600 : 500,
              color: activeTab === tab.key ? DesignTokens.colors.primary : DesignTokens.colors.text.muted,
              borderBottom: `3px solid ${activeTab === tab.key ? DesignTokens.colors.primary : 'transparent'}`,
              cursor: 'pointer',
              marginBottom: -1,
              fontFamily: DesignTokens.fonts.body,
              transition: 'all 0.2s',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>
      
      {activeTab === 'overview' && task && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <Card>
            <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '20px', fontFamily: DesignTokens.fonts.display, color: DesignTokens.colors.text.primary }}>任务信息</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }}>
              <div style={{ padding: '16px', background: DesignTokens.colors.background, borderRadius: DesignTokens.radii.md }}>
                <div style={{ fontSize: '12px', color: DesignTokens.colors.text.muted, marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>任务ID</div>
                <div style={{ fontFamily: DesignTokens.fonts.mono, fontSize: '14px', color: DesignTokens.colors.text.primary }}>{task.id}</div>
              </div>
              <div style={{ padding: '16px', background: DesignTokens.colors.background, borderRadius: DesignTokens.radii.md }}>
                <div style={{ fontSize: '12px', color: DesignTokens.colors.text.muted, marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>创建者</div>
                <div style={{ fontSize: '14px', color: DesignTokens.colors.text.primary }}>{task.owner_id || '系统'}</div>
              </div>
              <div style={{ padding: '16px', background: DesignTokens.colors.background, borderRadius: DesignTokens.radii.md }}>
                <div style={{ fontSize: '12px', color: DesignTokens.colors.text.muted, marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>创建时间</div>
                <div style={{ fontSize: '14px', color: DesignTokens.colors.text.primary }}>{new Date(task.created_at).toLocaleString('zh-CN', { hour12: false })}</div>
              </div>
              <div style={{ padding: '16px', background: DesignTokens.colors.background, borderRadius: DesignTokens.radii.md }}>
                <div style={{ fontSize: '12px', color: DesignTokens.colors.text.muted, marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>完成时间</div>
                <div style={{ fontSize: '14px', color: DesignTokens.colors.text.primary }}>{task.completed_at ? new Date(task.completed_at).toLocaleString('zh-CN', { hour12: false }) : '-'}</div>
              </div>
            </div>
          </Card>
          
          {task.target_patent && (
          <Card>
            <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '20px', fontFamily: DesignTokens.fonts.display, color: DesignTokens.colors.text.primary }}>目标专利</h3>
            <div style={{ display: 'flex', alignItems: 'center', gap: '20px', marginBottom: '20px' }}>
              <IconBox bg={DesignTokens.colors.iconBg.blue} size={56}>
                <Icons.File size={28} color={DesignTokens.colors.primary} />
              </IconBox>
              <div>
                <div style={{ fontWeight: 600, fontSize: '17px', color: DesignTokens.colors.text.primary }}>{task.target_patent.title}</div>
                <div style={{ fontSize: '14px', color: DesignTokens.colors.text.muted, marginTop: '4px' }}>
                  {task.target_patent.publication_no || task.target_patent.application_no || '未知专利号'}
                </div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '24px', fontSize: '14px' }}>
              <div>
                <span style={{ color: DesignTokens.colors.text.muted }}>IPC: </span>
                <Badge variant="accent">{task.target_patent.ipc || 'N/A'}</Badge>
              </div>
              {task.target_patent.claims && (
              <div>
                <span style={{ color: DesignTokens.colors.text.muted }}>权利要求: </span>
                <span style={{ fontWeight: 600 }}>{task.target_patent.claims.length} 项</span>
              </div>
              )}
            </div>
          </Card>
          )}
          
          <Card>
            <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '20px', fontFamily: DesignTokens.fonts.display, color: DesignTokens.colors.text.primary }}>比对库配置</h3>
            <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
              <IconBox bg={DesignTokens.colors.iconBg.amber} size={48}>
                <Icons.Library size={24} color={DesignTokens.colors.accent} />
              </IconBox>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: '16px', color: DesignTokens.colors.text.primary }}>{getLibraryName()}</div>
                <div style={{ fontSize: '14px', color: DesignTokens.colors.text.muted }}>
                  库ID: {task.library_id}
                </div>
              </div>
            </div>
          </Card>
          
          {task.result && (
            <Card style={{ background: DesignTokens.colors.surface, border: `2px solid ${DesignTokens.colors.success}40` }}>
              <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '24px', fontFamily: DesignTokens.fonts.display, color: DesignTokens.colors.text.primary }}>分析结果摘要</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '28px' }}>
                <div style={{ textAlign: 'center', padding: '20px', background: 'white', borderRadius: DesignTokens.radii.md }}>
                  <div style={{ fontSize: '36px', fontWeight: 700, color: DesignTokens.colors.primary, fontFamily: DesignTokens.fonts.display }}>{task.result.total_compared || 0}</div>
                  <div style={{ fontSize: '14px', color: DesignTokens.colors.text.muted, marginTop: '4px' }}>比对专利数</div>
                </div>
                <div style={{ textAlign: 'center', padding: '20px', background: 'white', borderRadius: DesignTokens.radii.md }}>
                  <div style={{ fontSize: '36px', fontWeight: 700, color: DesignTokens.colors.success, fontFamily: DesignTokens.fonts.display }}>{task.result.top_matches || 0}</div>
                  <div style={{ fontSize: '14px', color: DesignTokens.colors.text.muted, marginTop: '4px' }}>相似专利</div>
                </div>
                <div style={{ textAlign: 'center', padding: '20px', background: 'white', borderRadius: DesignTokens.radii.md }}>
                  <div style={{ fontSize: '36px', fontWeight: 700, color: DesignTokens.colors.error, fontFamily: DesignTokens.fonts.display }}>{Math.round(task.result.highest_score || 0)}%</div>
                  <div style={{ fontSize: '14px', color: DesignTokens.colors.text.muted, marginTop: '4px' }}>最高相似度</div>
                </div>
              </div>
              
              {task.result.top_results && task.result.top_results.length > 0 && (
              <>
              <h4 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '16px', color: DesignTokens.colors.text.primary }}>Top {Math.min(3, task.result.top_results.length)} 相似专利</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {task.result.top_results.slice(0, 3).map((result, index) => (
                  <div 
                    key={index}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '16px',
                      padding: '16px 20px',
                      background: 'white',
                      borderRadius: DesignTokens.radii.md,
                      boxShadow: DesignTokens.shadows.sm,
                    }}
                  >
                    <div style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: DesignTokens.radii.full,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '14px',
                      fontWeight: 600,
                      background: index === 0 ? '#f1f5f9' : '#f8fafc',
                      color: index === 0 ? DesignTokens.colors.text.primary : DesignTokens.colors.text.muted,
                      border: `1px solid ${DesignTokens.colors.border}`,
                    }}>
                      {index + 1}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600, color: DesignTokens.colors.text.primary }}>{result.title || result.patent_title}</div>
                      <div style={{ fontSize: '13px', color: DesignTokens.colors.text.muted }}>{result.publication_no || result.patent_number}</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '22px', fontWeight: 700, color: (result.similarity_score || result.similarity) >= 0.9 ? DesignTokens.colors.error : DesignTokens.colors.warning, fontFamily: DesignTokens.fonts.display }}>
                        {Math.round((result.similarity_score || result.similarity) * 100)}%
                      </div>
                      <Badge variant={(result.risk_level || result.risk) === 'high' ? 'red' : (result.risk_level || result.risk) === 'medium' ? 'yellow' : 'green'} size="sm">
                        {(result.risk_level || result.risk) === 'high' ? '高风险' : (result.risk_level || result.risk) === 'medium' ? '中风险' : '低风险'}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
              </>
              )}
              
              <Button 
                style={{ width: '100%', marginTop: '24px' }}
                onClick={() => {
                  if (task.result?.report_path) {
                    window.open(`http://localhost:8000/${task.result.report_path}`, '_blank')
                  } else {
                    alert('报告尚未生成')
                  }
                }}
              >
                查看完整分析结果
              </Button>
            </Card>
          )}
        </div>
      )}
      
      {activeTab === 'stages' && task && (
        <Card>
          <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '24px', fontFamily: DesignTokens.fonts.display, color: DesignTokens.colors.text.primary }}>执行阶段详情</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {task.stages && task.stages.length > 0 ? task.stages.map((stage, index) => (
              <div 
                key={stage.name || index}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '20px',
                  padding: '20px',
                  background: DesignTokens.colors.background,
                  borderRadius: DesignTokens.radii.md,
                }}
              >
                <div style={{
                  width: '48px',
                  height: '48px',
                  borderRadius: DesignTokens.radii.full,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: stage.status === 'completed' ? DesignTokens.colors.success : stage.status === 'running' ? DesignTokens.colors.warning : DesignTokens.colors.text.muted,
                  color: 'white',
                  fontSize: '20px',
                  fontWeight: 700,
                boxShadow: DesignTokens.shadows.icon,
              }}>
                {stage.status === 'completed' ? <Icons.Check size={20} color="white" /> : stage.status === 'running' ? <Icons.Loader size={20} color="white" /> : <Icons.Clock size={20} color="white" />}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '6px' }}>
                  <span style={{ fontWeight: 600, fontSize: '15px', color: DesignTokens.colors.text.primary }}>{stage.label || stage.name}</span>
                  <Badge variant={stage.status === 'completed' ? 'green' : stage.status === 'running' ? 'yellow' : 'secondary'} size="sm">
                    {stage.status === 'completed' ? '完成' : stage.status === 'running' ? '进行中' : '等待'}
                  </Badge>
                  </div>
                  {stage.detail && (
                  <div style={{ fontSize: '14px', color: DesignTokens.colors.text.muted }}>
                    {stage.detail}
                  </div>
                  )}
                </div>
                {stage.duration && (
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '16px', fontWeight: 600, color: DesignTokens.colors.text.primary }}>{stage.duration}秒</div>
                </div>
                )}
              </div>
            )) : (
              <div style={{ textAlign: 'center', padding: '40px', color: DesignTokens.colors.text.muted }}>
                暂无执行阶段信息
              </div>
            )}
          </div>
        </Card>
      )}
      
      {activeTab === 'logs' && task && (
        <Card>
          <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '24px', fontFamily: DesignTokens.fonts.display, color: DesignTokens.colors.text.primary }}>执行日志</h3>
          <div style={{
            background: DesignTokens.colors.primaryDark,
            borderRadius: DesignTokens.radii.lg,
            padding: '20px',
            fontFamily: DesignTokens.fonts.mono,
            fontSize: '13px',
            maxHeight: '500px',
            overflow: 'auto',
          }}>
            {task.logs && task.logs.length > 0 ? task.logs.map((log, index) => (
              <div 
                key={index}
                style={{
                  display: 'flex',
                  gap: '16px',
                  marginBottom: '10px',
                  color: log.level === 'error' ? '#ef4444' : log.level === 'warning' ? '#f59e0b' : '#94a3b8',
                }}
              >
                <span style={{ color: '#64748b', minWidth: '70px' }}>{log.time || new Date(log.timestamp).toLocaleTimeString()}</span>
                <span style={{ color: DesignTokens.colors.accent, minWidth: '90px' }}>[{log.stage || 'system'}]</span>
                <span>{log.message}</span>
              </div>
            )) : (
              <div style={{ textAlign: 'center', padding: '40px', color: '#64748b' }}>
                暂无日志信息
              </div>
            )}
          </div>
        </Card>
      )}
      
      {activeTab === 'config' && task && (
        <Card>
          <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '24px', fontFamily: DesignTokens.fonts.display, color: DesignTokens.colors.text.primary }}>算法配置</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div>
              <div style={{ fontSize: '15px', fontWeight: 600, marginBottom: '16px', color: DesignTokens.colors.text.primary }}>特征权重配置</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                {[
                  { label: '技术领域', value: 15, color: '#8b5cf6' },
                  { label: '技术问题', value: 20, color: '#06b6d4' },
                  { label: '技术方案', value: 45, color: '#f59e0b' },
                  { label: '技术效果', value: 20, color: '#10b981' },
                ].map((item) => (
                  <div key={item.label}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px', marginBottom: '8px' }}>
                      <span style={{ color: DesignTokens.colors.text.secondary }}>{item.label}</span>
                      <span style={{ fontWeight: 700, color: item.color }}>{item.value}%</span>
                    </div>
                    <div style={{ height: '10px', background: DesignTokens.colors.border, borderRadius: DesignTokens.radii.full }}>
                      <div style={{ width: `${item.value}%`, height: '100%', background: item.color, borderRadius: DesignTokens.radii.full }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Card>
      )}
      
      <Modal 
        isOpen={showCancelModal} 
        onClose={() => setShowCancelModal(false)}
        title="取消任务"
      >
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <div style={{ margin: '0 auto 24px' }}>
            <IconBox bg={DesignTokens.colors.errorLight} size={64} hover={false}>
              <Icons.Alert size={28} color={DesignTokens.colors.error} />
            </IconBox>
          </div>
          <p style={{ fontSize: '16px', marginBottom: '28px', color: DesignTokens.colors.text.secondary, lineHeight: 1.6 }}>
            确定要取消任务 <strong style={{ color: DesignTokens.colors.text.primary }}>{task?.name}</strong> 吗？<br/>
            取消后任务将停止执行，已产生的费用不予退还。
          </p>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
            <Button variant="secondary" onClick={() => setShowCancelModal(false)}>
              保留任务
            </Button>
            <Button variant="ghost" onClick={() => {
              setShowCancelModal(false)
              alert('任务已取消')
            }} style={{ color: DesignTokens.colors.error }}>
              确认取消
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

// ==================== 新建任务向导 ====================
const NewTask = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const [step, setStep] = useState(1)
  const [taskName, setTaskName] = useState('')
  const [uploadedFile, setUploadedFile] = useState(null)
  const [parsedPatent, setParsedPatent] = useState(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isParsing, setIsParsing] = useState(false)
  const [selectedLibrary, setSelectedLibrary] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [libraries, setLibraries] = useState([])
  const [loadingLibraries, setLoadingLibraries] = useState(true)
  
  // Fetch libraries from API
  useEffect(() => {
    const fetchLibraries = async () => {
      try {
        setLoadingLibraries(true)
        const data = await api.libraries.list()
        setLibraries(data)
      } catch (error) {
        console.error('Failed to fetch libraries:', error)
      } finally {
        setLoadingLibraries(false)
      }
    }
    fetchLibraries()
  }, [])
  
  const handleFileSelect = (files) => {
    // Handle both single file and array of files
    const file = Array.isArray(files) ? files[0] : files
    
    if (!file) {
      console.error('No file selected')
      return
    }
    
    if (file.size > 50 * 1024 * 1024) {
      alert('文件大小超过50MB限制')
      return
    }
    
    setUploadedFile(file)
    setIsUploading(true)
    setUploadProgress(0)
    
    let progress = 0
    const interval = setInterval(() => {
      progress += 10
      setUploadProgress(progress)
      if (progress >= 100) {
        clearInterval(interval)
        setIsUploading(false)
        startParsing(file)
      }
    }, 200)
  }
  
  const startParsing = (file) => {
    setIsParsing(true)
    setTimeout(() => {
      setIsParsing(false)
      setParsedPatent({
        title: file.name.replace(/\.[^/.]+$/, ''),
        ipc: 'H04N21/43',
        claims: 12,
        quality: 95,
      })
      if (!taskName) {
        setTaskName(file.name.replace(/\.[^/.]+$/, '') + '分析')
      }
    }, 2000)
  }
  
  const handleSubmit = async () => {
    if (!taskName.trim() || !parsedPatent || !selectedLibrary) {
      alert('请填写完整信息')
      return
    }
    
    setIsSubmitting(true)
    
    try {
      // Step 1: Create analysis task first (without target patent)
      console.log('Creating task...')
      const taskResult = await api.tasks.create({
        name: taskName,
        library_id: selectedLibrary.id,
      })
      console.log('Task created:', taskResult)
      
      // Step 2: Upload target patent file
      console.log('Uploading target patent...')
      const uploadResult = await api.upload.file(uploadedFile)
      console.log('Upload result:', uploadResult)
      
      // Step 3: Parse the patent
      const parseResult = await api.upload.parse(uploadResult.file_id)
      console.log('Parse result:', parseResult)
      
      // Step 4: Save patent to the library
      const saveResult = await api.upload.save({
        file_id: uploadResult.file_id,
        library_id: selectedLibrary.id,
        patent_info: parseResult.patent_info,
        quality_score: parseResult.quality_score,
      })
      console.log('Save result:', saveResult)
      
      // Step 5: Submit task with target patent
      console.log('Submitting task with target patent...')
      await api.tasks.submit(taskResult.id, saveResult.id)
      console.log('Task submitted successfully')
      
      // Navigate to the new task
      navigate(`/tasks/${taskResult.id}`)
    } catch (error) {
      console.error('Failed to create task:', error)
      alert('创建任务失败: ' + error.message)
      setIsSubmitting(false)
    }
  }
  
  const steps = [
    { num: 1, label: '上传专利' },
    { num: 2, label: '选择库' },
    { num: 3, label: '确认提交' },
  ]
  
  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '48px 32px' }}>
      <div style={{ marginBottom: '48px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '20px' }}>
          {steps.map((s, i) => (
            <React.Fragment key={i}>
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '10px',
              }}>
                <div style={{
                  width: '48px',
                  height: '48px',
                  borderRadius: DesignTokens.radii.full,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 700,
                  fontSize: '18px',
                  background: step >= s.num ? DesignTokens.colors.primary : DesignTokens.colors.background,
                  color: step >= s.num ? 'white' : DesignTokens.colors.text.muted,
                  border: `2px solid ${step >= s.num ? DesignTokens.colors.primary : DesignTokens.colors.border}`,
                  boxShadow: step >= s.num ? DesignTokens.shadows.icon : 'none',
                }}>
                  {step > s.num ? (
                    <Icons.Check size={20} color="white" />
                  ) : s.num}
                </div>
                <span style={{ fontSize: '14px', fontWeight: step >= s.num ? 600 : 500, color: step >= s.num ? DesignTokens.colors.primary : DesignTokens.colors.text.muted }}>
                  {s.label}
                </span>
              </div>
              {i < 2 && (
                <div style={{
                  width: '80px',
                  height: '3px',
                  background: step > s.num ? DesignTokens.colors.primary : DesignTokens.colors.border,
                  borderRadius: DesignTokens.radii.full,
                }} />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
      
      {step === 1 && (
        <Card>
          <h2 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '10px', fontFamily: DesignTokens.fonts.display, color: DesignTokens.colors.primary }}>上传目标专利</h2>
          <p style={{ fontSize: '15px', color: DesignTokens.colors.text.secondary, marginBottom: '28px' }}>
            上传需要分析的专利文件，系统将自动解析专利内容
          </p>
          
          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '10px', color: DesignTokens.colors.text.primary }}>
              任务名称
            </label>
            <input
              type="text"
              value={taskName}
              onChange={(e) => setTaskName(e.target.value)}
              placeholder="输入任务名称..."
              style={{
                width: '100%',
                padding: '14px 18px',
                border: `1px solid ${DesignTokens.colors.border}`,
                borderRadius: DesignTokens.radii.md,
                fontSize: '15px',
                fontFamily: DesignTokens.fonts.body,
                outline: 'none',
              }}
            />
          </div>
          
          {!parsedPatent && (
            <div style={{ marginBottom: '28px' }}>
              {isUploading ? (
                <div style={{ textAlign: 'center', padding: '48px' }}>
                  <div style={{ marginBottom: '20px' }}>
                    <IconBox bg={DesignTokens.colors.iconBg.blue} size={64} hover={false}>
                      <Icons.Refresh size={32} color={DesignTokens.colors.primary} />
                    </IconBox>
                  </div>
                  <p style={{ fontSize: '18px', fontWeight: 600, marginBottom: '20px', color: DesignTokens.colors.text.primary }}>
                    正在上传 {uploadedFile?.name}
                  </p>
                  <ProgressBar progress={uploadProgress} />
                  <p style={{ fontSize: '15px', color: DesignTokens.colors.text.muted, marginTop: '12px' }}>
                    {uploadProgress}%
                  </p>
                </div>
              ) : isParsing ? (
                <div style={{ textAlign: 'center', padding: '48px' }}>
                  <div style={{ marginBottom: '20px' }}>
                    <IconBox bg={DesignTokens.colors.iconBg.blue} size={64} hover={false}>
                      <Icons.File size={32} color={DesignTokens.colors.primary} />
                    </IconBox>
                  </div>
                  <p style={{ fontSize: '18px', fontWeight: 600, marginBottom: '10px', color: DesignTokens.colors.text.primary }}>
                    正在解析专利...
                  </p>
                  <p style={{ fontSize: '14px', color: DesignTokens.colors.text.muted }}>
                    识别专利结构 | 提取权利要求 | 分析技术特征
                  </p>
                </div>
              ) : (
                <FileUploader onFileSelect={handleFileSelect} />
              )}
            </div>
          )}
          
          {parsedPatent && (
            <div style={{
              padding: '24px',
              background: `${DesignTokens.colors.success}08`,
              borderRadius: DesignTokens.radii.lg,
              border: `2px solid ${DesignTokens.colors.success}30`,
              marginBottom: '28px',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  background: DesignTokens.colors.success,
                  borderRadius: DesignTokens.radii.full,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '18px',
                boxShadow: DesignTokens.shadows.icon,
              }}>
                <Icons.Check size={16} color="white" />
              </div>
              <span style={{ fontWeight: 600, color: DesignTokens.colors.success, fontSize: '15px' }}>解析完成</span>
              </div>
              <div style={{ marginBottom: '14px' }}>
                <span style={{ color: DesignTokens.colors.text.muted }}>专利标题: </span>
                <span style={{ fontWeight: 600, color: DesignTokens.colors.text.primary }}>{parsedPatent.title}</span>
              </div>
              <div style={{ marginBottom: '14px' }}>
                <span style={{ color: DesignTokens.colors.text.muted }}>IPC分类: </span>
                <Badge variant="accent">{parsedPatent.ipc}</Badge>
              </div>
              <div style={{ marginBottom: '14px' }}>
                <span style={{ color: DesignTokens.colors.text.muted }}>权利要求: </span>
                <span style={{ fontWeight: 600 }}>{parsedPatent.claims} 项</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span style={{ color: DesignTokens.colors.text.muted }}>解析质量: </span>
                <div style={{ flex: 1, maxWidth: '180px' }}>
                  <ProgressBar progress={parsedPatent.quality} size="sm" />
                </div>
                <span style={{ fontWeight: 700, color: DesignTokens.colors.success }}>{parsedPatent.quality} 分</span>
              </div>
            </div>
          )}
          
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
            <Button variant="secondary" onClick={() => navigate('/')}>
              取消
            </Button>
            <Button onClick={() => setStep(2)} disabled={!parsedPatent}>
              下一步 →
            </Button>
          </div>
        </Card>
      )}
      
      {step === 2 && (
        <Card>
          <h2 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '10px', fontFamily: DesignTokens.fonts.display, color: DesignTokens.colors.primary }}>选择比对库</h2>
          <p style={{ fontSize: '15px', color: DesignTokens.colors.text.secondary, marginBottom: '28px' }}>
            基于您的专利IPC分类 {parsedPatent?.ipc}，推荐以下库
          </p>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '28px' }}>
            {libraries.map((lib) => (
              <div
                key={lib.id}
                onClick={() => setSelectedLibrary(lib)}
                style={{
                  padding: '20px',
                  borderRadius: DesignTokens.radii.lg,
                  border: `2px solid ${selectedLibrary?.id === lib.id ? DesignTokens.colors.primary : DesignTokens.colors.border}`,
                  background: selectedLibrary?.id === lib.id ? `${DesignTokens.colors.primary}08` : 'white',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{
                    width: '24px',
                    height: '24px',
                    borderRadius: DesignTokens.radii.full,
                    border: `2px solid ${selectedLibrary?.id === lib.id ? DesignTokens.colors.primary : DesignTokens.colors.border}`,
                    background: selectedLibrary?.id === lib.id ? DesignTokens.colors.primary : 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}>
                    {selectedLibrary?.id === lib.id && (
                      <Icons.Check size={14} color="white" />
                    )}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: '16px', marginBottom: '4px', color: DesignTokens.colors.text.primary }}>{lib.name}</div>
                    <div style={{ fontSize: '14px', color: DesignTokens.colors.text.muted }}>
                      {lib.patent_count || 0}份专利
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
            <Button variant="secondary" onClick={() => setStep(1)}>
              ← 上一步
            </Button>
            <Button onClick={() => setStep(3)} disabled={!selectedLibrary}>
              下一步 →
            </Button>
          </div>
        </Card>
      )}
      
      {step === 3 && (
        <Card>
          <h2 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '28px', fontFamily: DesignTokens.fonts.display, color: DesignTokens.colors.primary }}>确认任务信息</h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '28px' }}>
            <div style={{ padding: '20px', background: DesignTokens.colors.background, borderRadius: DesignTokens.radii.md }}>
              <div style={{ fontSize: '12px', color: DesignTokens.colors.text.muted, marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>任务名称</div>
              <div style={{ fontWeight: 600, fontSize: '16px', color: DesignTokens.colors.text.primary }}>{taskName}</div>
            </div>
            
            <div style={{ padding: '20px', background: DesignTokens.colors.background, borderRadius: DesignTokens.radii.md }}>
              <div style={{ fontSize: '12px', color: DesignTokens.colors.text.muted, marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>目标专利</div>
              <div style={{ fontWeight: 600, fontSize: '16px', color: DesignTokens.colors.text.primary }}>{parsedPatent?.title}</div>
              <div style={{ fontSize: '14px', color: DesignTokens.colors.text.muted, marginTop: '6px' }}>
                IPC: {parsedPatent?.ipc} · 权利要求: {parsedPatent?.claims}项
              </div>
            </div>
            
            <div style={{ padding: '20px', background: DesignTokens.colors.background, borderRadius: DesignTokens.radii.md }}>
              <div style={{ fontSize: '12px', color: DesignTokens.colors.text.muted, marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>比对库</div>
              <div style={{ fontWeight: 600, fontSize: '16px', color: DesignTokens.colors.text.primary }}>{selectedLibrary?.name}</div>
              <div style={{ fontSize: '14px', color: DesignTokens.colors.text.muted, marginTop: '6px' }}>
                {selectedLibrary?.patent_count || 0}份专利
              </div>
            </div>
          </div>
          
          <div style={{ padding: '20px', background: `${DesignTokens.colors.accent}06`, borderRadius: DesignTokens.radii.md, marginBottom: '28px', border: `1px solid ${DesignTokens.colors.accent}20` }}>
            <div style={{ fontSize: '15px', fontWeight: 600, color: DesignTokens.colors.accentDark, marginBottom: '12px' }}>
              预估信息
            </div>
            <ul style={{ fontSize: '14px', color: DesignTokens.colors.text.secondary, paddingLeft: '20px', lineHeight: 1.8 }}>
              <li>处理时间: 约 30-60 秒</li>
              <li>预估费用: ¥0.12</li>
              <li>结果数量: Top 20 相似专利</li>
            </ul>
          </div>
          
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
            <Button variant="secondary" onClick={() => setStep(2)}>
              ← 上一步
            </Button>
            <Button onClick={handleSubmit} disabled={isSubmitting}>
              {isSubmitting ? '提交中...' : '提交任务'}
            </Button>
          </div>
        </Card>
      )
      }
    </div>
  )
}

// ==================== Main App ====================
function App() {
  return (
    <BrowserRouter>
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: DesignTokens.colors.background }}>
        <Routes>
          <Route path="/" element={<><Header /><Dashboard /></>} />
          <Route path="/tasks" element={<><Header /><TaskList /></>} />
          <Route path="/tasks/new" element={<><Header /><NewTask /></>} />
          <Route path="/tasks/:id" element={<><Header /><TaskDetail /></>} />
          <Route path="/libraries" element={<><Header /><LibraryManagement /></>} />
          <Route path="/libraries/:id" element={<><Header /><LibraryDetail /></>} />
          <Route path="/api-test" element={<ApiTest />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
