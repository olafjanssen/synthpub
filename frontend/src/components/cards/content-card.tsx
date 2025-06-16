import { ContentData } from "@/utils/types";
import Image from "next/image";
import Bg1 from "@/assets/images/bg-1.png";
import Bg2 from "@/assets/images/bg-2.png";
import Bg3 from "@/assets/images/bg-3.png";
import Bg4 from "@/assets/images/bg-4.png";
import Bg5 from "@/assets/images/bg-5.png";

interface Props {
	data: ContentData;
	count: number;
	borderColor: string;
	hoverColor?: string;
}

const ContentCard: React.FC<Props> = ({
	data,
	count,
	borderColor = "#f06e6c",
	hoverColor = "grayscale",
}) => {
	const images = [Bg1, Bg2, Bg3, Bg4, Bg5];
	const selectedImage = images[count % images.length];

	//TODO: needed to use symbol instead of star
	return (
		<div
			className={`w-56 shadow-[0.3em_0.3em_0px_#4a6a5f] flex flex-col bg-darkGreen text-[#627035] p-2  cursor-pointer hover:${hoverColor}`}
		>
			<Image className="h-56" src={selectedImage} alt="card image" />
			<div className="p-2 flex flex-col relative">
				<h5
					className={`w-[16ch] overflow-hidden whitespace-nowrap text-ellipsis text-base font-bold text-[#627035] uppercase flex justify-between items-center `}
				>
					{data.title}
				</h5>
			</div>
			<div className={`p-2 border-t-2 border-[${borderColor}] h-20`}>
				<p className=" text-[#627035]leading-5 font-bold overflow-hidden line-clamp-2">
					{data.description}
				</p>
			</div>
		</div>
	);
};

export default ContentCard;
