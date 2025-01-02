import { UserButton, auth } from "@clerk/nextjs";
import Link from "next/link";
import { checkSubscription } from "@/lib/checkSubscription";
import PricingButton from "./components/PricingButton";

const Navbar = async () => {
  const { userId } = await auth();
  const isAuth = !!userId;
  const isPro = await checkSubscription({ userId });

  return (
    <nav className="shadow-sm sticky top-0 left-0 right-0 z-30 bg-gradient-to-r from-purple-100 via-pink-100 to-purple-100 h-20">
      <div className="max-w-5xl mx-auto h-full flex justify-between items-center px-4">
        <a href="/" className="text-purple-800 font-bold text-xl tracking-tight hover:text-pink-600 transition-colors">
          PDF AI Assistant
        </a>
        <div className="flex items-center flex-wrap gap-8">
          <Link
            href="/"
            className="text-purple-800 hover:text-pink-600 font-medium transition-colors"
          >
            Home
          </Link>
          <Link
            href="/chat"
            className="text-purple-800 hover:text-pink-600 font-medium transition-colors"
          >
            Chat
          </Link>

          {isAuth ? (
            <div className="ml-2">
              <UserButton afterSignOutUrl="/" />
            </div>
          ) : (
            <Link href={"/sign-up"}>
              <div className="bg-purple-600 text-white px-5 py-2 rounded-lg hover:bg-pink-600 transition-all duration-200 font-medium">
                Sign Up
              </div>
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
