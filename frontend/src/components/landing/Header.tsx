import React from 'react'

export default function Header() {
	return (
		<header className="p-4 border-b border-white/10">
			<div className="max-w-6xl mx-auto flex items-center justify-between">
				<h1 className="text-xl font-bold text-white">엔오건강도우미</h1>
				<nav className="text-sm text-gray-300">융합 분석 데모</nav>
			</div>
		</header>
	)
}