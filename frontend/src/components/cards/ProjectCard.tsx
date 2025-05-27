import { Project } from "@/features/dashboard";
import Image from "next/image";
import Bg1 from "@/assets/images/bg-1.png";
import Bg2 from "@/assets/images/bg-2.png";
import Bg3 from "@/assets/images/bg-3.png";
import Bg4 from "@/assets/images/bg-4.png";
import Bg5 from "@/assets/images/bg-5.png";

interface Props {
	project: Project;
	count: number;
}

const ProjectCard: React.FC<Props> = ({ project, count }) => {
	const images = [Bg1, Bg2, Bg3, Bg4, Bg5];
	const selectedImage = images[count % images.length];

	return (
		<div className="w-56 shadow-[0.3em_0.3em_0px_#4a6a5f] flex flex-col bg-darkGreen text-[#627035] p-2 hover:grayscale cursor-pointer">
			<Image className="h-56" src={selectedImage} alt="card image" />
			<div className="p-2 flex flex-col relative">
				<h5 className="w-[16ch] overflow-hidden whitespace-nowrap text-ellipsis text-base font-bold text-[#627035] uppercase flex justify-between items-center after:content-['✱'] after:ml-2 after:text-[1rem] after:inline-block after:absolute after:top-2 after:right-3 after:scale-125">
					{project.title}
				</h5>
			</div>
			<div className="p-2 border-t-2 border-[#93b39c38] h-20">
				<p className=" text-[#627035]leading-5 font-bold overflow-hidden line-clamp-2">
					{project.description}
				</p>
			</div>
		</div>
	);
};

export default ProjectCard;
