import hre from "hardhat";

async function main() {
  console.log("Testing Hardhat setup...");
  console.log("HRE keys:", Object.keys(hre));

  // Try to get ethers
  try {
    const ethers = (hre as any).ethers;
    if (ethers) {
      console.log("✅ Ethers found!");
      const signers = await ethers.getSigners();
      console.log("Deployer:", signers[0].address);

      // Deploy a simple test token
      const TestUSDC = await ethers.getContractFactory("TestUSDC");
      console.log("Deploying TestUSDC...");
      const tUSDC = await TestUSDC.deploy();
      await tUSDC.waitForDeployment();
      const address = await tUSDC.getAddress();
      console.log("✅ TestUSDC deployed at:", address);

    } else {
      console.log("❌ Ethers not found in hre");
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
