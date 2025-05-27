interface Props {
	title: string;
	onClick?: () => void;
	className?: string;
}

const Button: React.FC<Props> = ({ title, onClick, className }) => {
	return (
		<button
			onClick={onClick}
			className={`bg-[#AEB71D] text-black px-4 py-1 rounded-md hover:bg-[#a3ab35] transition-colors  ${className}`}
		>
			{title}
		</button>
	);
};

export default Button;
