interface Props {
	onClose: () => void;
	title: string;
	children: React.ReactNode;
}

const Modal: React.FC<Props> = ({ title, onClose, children }) => {
	return (
		<div
			onClick={onClose}
			className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
		>
			<div
				onClick={(e) => e.stopPropagation()}
				className="relative w-full max-w-2xl p-6 rounded-md shadow-2xl bg-[#4A6A5F] text-white  overflow-y-auto"
			>
				<button
					onClick={onClose}
					className="absolute top-3 right-3 text-2xl font-bold"
				>
					&times;
				</button>

				<h2 className="text-3xl font-semibold mb-4">{title}</h2>

				<span className="flex mb-4 border-b border-[#b3d9bb]"></span>
				{children}
			</div>
		</div>
	);
};

export default Modal;
