import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

export type AccordionDetailsProps = {
	title: string;
	subtitle?: string;
	children: React.ReactNode;
};

const AccordionDetails = ({
	title,
	subtitle,
	children,
}: AccordionDetailsProps) => {
	const [isOpen, setIsOpen] = useState(false);

	return (
		<div
			className={`transition-all duration-200 ${
				isOpen ? "border-blue-500 border-l-4" : ""
			}`}
		>
			<button
				onClick={() => setIsOpen(!isOpen)}
				className="w-full rounded-xl flex justify-between items-center px-4 py-3 bg-white hover:bg-gray-100 transition-all duration-200"
			>
				<div className="text-left flex gap-2 items-center">
					<div className="text-sm font-bold text-gray-800">{title}</div>
					<div className="text-xs text-gray-500">{subtitle}</div>
				</div>
				<div className="text-xl font-light text-gray-500">
					{isOpen ? "▲" : "▼"}
				</div>
			</button>

			<AnimatePresence>
				{isOpen && (
					<motion.div
						initial={{ height: 0, opacity: 0 }}
						animate={{ height: "auto", opacity: 1 }}
						exit={{ height: 0, opacity: 0 }}
						transition={{ duration: 0.3 }}
						className="overflow-hidden px-4  text-gray-700 text-sm"
					>
						{children}
					</motion.div>
				)}
			</AnimatePresence>
		</div>
	);
};

export default AccordionDetails;
