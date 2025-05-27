/* eslint-disable @typescript-eslint/no-explicit-any */
import Image from "next/image";

interface TopCardProps {
	imageSrc?: any;
	title?: string;
	subtitle?: string;
	bgColor?: string;
	href?: string;
	textColor?: string;
	onClick?: () => void;
}

const TopCard: React.FC<TopCardProps> = ({
	imageSrc,
	title,
	subtitle,
	href,
	bgColor = "bg-topCardBg",
	textColor = "text-[#b3d9bb]",
	onClick,
}) => {
	const subtitleLines = subtitle ? subtitle.split("\n").filter(Boolean) : [];
	const isMultiLine = subtitleLines.length > 1;
	const cardContent = (
		<div
			className={`p-2 w-56 flex flex-col rounded-none shadow-[0.3em_0.3em_0px_#4a6a5f]  text-white cursor-pointer hover:filter hover:grayscale ${bgColor}`}
			onClick={onClick}
		>
			<div className="h-[13.5rem] p-2 pb-0 pt-0 pl-0 pr-0">
				{imageSrc ? (
					<Image
						src={imageSrc}
						alt="Card image"
						className="w-full object-contain"
					/>
				) : (
					<div className={`w-full h-full ${bgColor}`}></div>
				)}
			</div>
			<div className="p-2 pl-0 pr-0 flex flex-col flex-grow">
				{title && (
					<h4
						className={`text-[2rem] tracking-wide ${textColor} font-normal flex justify-between mb-0`}
					>
						{title}
					</h4>
				)}
				{subtitle && (
					<h6
						className={`relative capitalize text-[1rem] tracking-tight ${textColor} font-normal flex flex-col justify-between ${
							!title &&
							(isMultiLine
								? `after:content-['✱']  after:ml-2 after:text-[1rem] after:inline-block after:absolute after:top-2 after:right-[1.75rem] after:scale-[3.5]`
								: `after:content-['✱']  after:ml-2 after:text-[1rem] after:inline-block after:absolute after:top-0 after:right-3 after:scale-125`)
						}`}
					>
						{subtitleLines.map((line, index, arr) => (
							<span key={index}>
								{line}
								{index < arr.length - 1 && <br />}
							</span>
						))}
					</h6>
				)}
			</div>
			<div className="p-2 pl-0 pr-0 pb-0 border-t border-[#b3d9bb] h-20"></div>
		</div>
	);

	return href ? <a href={href}>{cardContent}</a> : cardContent;
};

export default TopCard;
