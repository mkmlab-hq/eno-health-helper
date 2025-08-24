import React from 'react'

export default function Footer() {
	return (
		<footer className="p-6 border-t border-white/10 text-center text-gray-400">
			<div className="max-w-6xl mx-auto">
				© {new Date().getFullYear()} ENO Health Helper. All rights reserved.
			</div>
		</footer>
	)
}