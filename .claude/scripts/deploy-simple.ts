import hre from "hardhat";
import {ethers, Contract, Wallet} from "ethers";
import fs from "fs";

async function main() {
  console.log("🚀 Deploying CredLend Protocol to Creditcoin Testnet...\n");

  // Setup provider and signer
  const provider = new ethers.JsonRpcProvider("https://rpc.cc3-testnet.creditcoin.network");
  const privateKey = process.env.PRIVATE_KEY;

  if (!privateKey) {
    throw new Error("PRIVATE_KEY environment variable is required");
  }

  const wallet = new Wallet(privateKey, provider);

  console.log("📍 Deploying from:", wallet.address);
  const balance = await provider.getBalance(wallet.address);
  console.log("💰 Balance:", ethers.formatEther(balance), "CTC\n");

  // Helper function to deploy contracts
  async function deployContract(name: string, args: any[] = []) {
    console.log(`Deploying ${name}...`);
    const artifact = await hre.artifacts.readArtifact(name);
    const factory = new ethers.ContractFactory(artifact.abi, artifact.bytecode, wallet);
    const contract = await factory.deploy(...args);
    await contract.waitForDeployment();
    const address = await contract.getAddress();
    console.log(`✅ ${name} deployed at: ${address}\n`);
    return {contract, address};
  }

  const deployedAddresses: any = {};

  // Deploy Test Tokens
  console.log("━━━━━━ TEST TOKENS ━━━━━━");
  const {address: tUSDC} = await deployContract("TestUSDC");
  const {address: tUSDT} = await deployContract("TestUSDT");
  const {address: tDAI} = await deployContract("TestDAI");
  const {address: tETH} = await deployContract("TestETH");
  const {address: tWBTC} = await deployContract("TestWBTC");

  deployedAddresses.testTokens = {tUSDC, tUSDT, tDAI, tETH, tWBTC};

  // Deploy CRED Token
  console.log("━━━━━━ CORE PROTOCOL ━━━━━━");
  const {address: credToken} = await deployContract("CredToken");
  deployedAddresses.credToken = credToken;

  // Deploy USC Attestor
  const {address: uscAttestor, contract: uscAttestorContract} = await deployContract("USCAttestor");
  deployedAddresses.uscAttestor = uscAttestor;

  // Deploy Credit Scoring
  const {address: creditScoring, contract: creditScoringContract} = await deployContract("CreditScoring");
  deployedAddresses.creditScoring = creditScoring;

  // Set USC Attestor
  console.log("Setting USC Attestor in CreditScoring...");
  const tx1 = await creditScoringContract.setUSCAttestor(uscAttestor);
  await tx1.wait();
  console.log("✅ USC Attestor configured\n");

  // Deploy Credit NFT
  const {address: creditNFT} = await deployContract("CreditNFT");
  deployedAddresses.creditNFT = creditNFT;

  // Deploy Interest Rate Strategy
  const {address: interestRateStrategy} = await deployContract("InterestRateStrategy", [creditScoring]);
  deployedAddresses.interestRateStrategy = interestRateStrategy;

  // Deploy Lending Pool FIRST
  console.log("━━━━━━ LENDING INFRASTRUCTURE ━━━━━━");
  const {address: lendingPool, contract: lendingPoolContract} = await deployContract("LendingPool", [
    credToken,
    creditScoring,
    interestRateStrategy
  ]);
  deployedAddresses.lendingPool = lendingPool;

  // Deploy ATokens and DebtTokens
  console.log("━━━━━━ TOKEN IMPLEMENTATIONS ━━━━━━");

  const assets = [
    {name: "tUSDC", address: tUSDC},
    {name: "tUSDT", address: tUSDT},
    {name: "tDAI", address: tDAI},
    {name: "tETH", address: tETH},
    {name: "tWBTC", address: tWBTC},
  ];

  deployedAddresses.aTokens = {};
  deployedAddresses.variableDebtTokens = {};
  deployedAddresses.stableDebtTokens = {};

  for (const asset of assets) {
    // Get decimals for the asset
    const contractName = asset.name === "tUSDC" ? "TestUSDC" :
                        asset.name === "tUSDT" ? "TestUSDT" :
                        asset.name === "tDAI" ? "TestDAI" :
                        asset.name === "tETH" ? "TestETH" : "TestWBTC";
    const tokenArtifact = await hre.artifacts.readArtifact(contractName);
    const tokenContract = new Contract(asset.address, tokenArtifact.abi, wallet);
    const decimals = await tokenContract.decimals();

    const {address: aToken} = await deployContract("AToken", [
      asset.address,
      lendingPool,
      `CredLend ${asset.name}`,
      `a${asset.name}`
    ]);
    deployedAddresses.aTokens[asset.name] = aToken;

    const {address: varDebt} = await deployContract("VariableDebtToken", [
      asset.address,
      lendingPool,
      `CredLend Variable Debt ${asset.name}`,
      `variableDebt${asset.name}`,
      decimals
    ]);
    deployedAddresses.variableDebtTokens[asset.name] = varDebt;

    const {address: stableDebt} = await deployContract("StableDebtToken", [
      asset.address,
      lendingPool,
      `CredLend Stable Debt ${asset.name}`,
      `stableDebt${asset.name}`,
      decimals
    ]);
    deployedAddresses.stableDebtTokens[asset.name] = stableDebt;
  }

  // Deploy Flash Loan
  const {address: flashLoan} = await deployContract("FlashLoan", [creditScoring]);
  deployedAddresses.flashLoan = flashLoan;

  // Deploy Governance
  console.log("━━━━━━ GOVERNANCE ━━━━━━");
  const {address: governor} = await deployContract("CredLendGovernor", [credToken]);
  deployedAddresses.governor = governor;

  // Deploy Safety Module
  const {address: safetyModule} = await deployContract("SafetyModule", [credToken]);
  deployedAddresses.safetyModule = safetyModule;

  // Configure roles
  console.log("━━━━━━ CONFIGURATION ━━━━━━");
  console.log("Granting roles...");

  const credTokenArtifact = await hre.artifacts.readArtifact("CredToken");
  const credTokenContract = new Contract(credToken, credTokenArtifact.abi, wallet);

  const creditNFTArtifact = await hre.artifacts.readArtifact("CreditNFT");
  const creditNFTContract = new Contract(creditNFT, creditNFTArtifact.abi, wallet);

  const MINTER_ROLE = await credTokenContract.MINTER_ROLE();
  const REWARDS_ROLE = await credTokenContract.REWARDS_ROLE();
  const SCORER_ROLE = await creditScoringContract.SCORER_ROLE();
  const UPDATER_ROLE = await creditNFTContract.UPDATER_ROLE();

  await (await credTokenContract.grantRole(MINTER_ROLE, lendingPool)).wait();
  await (await credTokenContract.grantRole(REWARDS_ROLE, lendingPool)).wait();
  await (await creditScoringContract.grantRole(SCORER_ROLE, lendingPool)).wait();
  await (await creditNFTContract.grantRole(MINTER_ROLE, creditScoring)).wait();
  await (await creditNFTContract.grantRole(UPDATER_ROLE, creditScoring)).wait();

  console.log("✅ Roles configured\n");

  // Initialize reserves
  console.log("Initializing reserves...");
  for (const asset of assets) {
    await (await lendingPoolContract.initReserve(
      asset.address,
      deployedAddresses.aTokens[asset.name],
      deployedAddresses.stableDebtTokens[asset.name],
      deployedAddresses.variableDebtTokens[asset.name],
      interestRateStrategy
    )).wait();
    console.log(`✅ ${asset.name} reserve initialized`);
  }

  // Save deployment addresses
  const deploymentData = {
    network: "creditcoin_testnet",
    chainId: 102031,
    deployer: wallet.address,
    timestamp: new Date().toISOString(),
    contracts: deployedAddresses
  };

  const deploymentsDir = "./deployments";
  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir, {recursive: true});
  }

  fs.writeFileSync(
    `${deploymentsDir}/creditcoin-testnet.json`,
    JSON.stringify(deploymentData, null, 2)
  );

  console.log("\n🎉 ========================");
  console.log("🎉 DEPLOYMENT COMPLETE!");
  console.log("🎉 ========================\n");

  console.log("📋 CONTRACT ADDRESSES:");
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");

  console.log("🪙 Test Tokens:");
  for (const [name, address] of Object.entries(deployedAddresses.testTokens)) {
    console.log(`  ${name}: ${address}`);
  }

  console.log("\n🏛️  Core Protocol:");
  console.log(`  CredToken: ${deployedAddresses.credToken}`);
  console.log(`  CreditScoring: ${deployedAddresses.creditScoring}`);
  console.log(`  USCAttestor: ${deployedAddresses.uscAttestor}`);
  console.log(`  CreditNFT: ${deployedAddresses.creditNFT}`);
  console.log(`  InterestRateStrategy: ${deployedAddresses.interestRateStrategy}`);
  console.log(`  LendingPool: ${deployedAddresses.lendingPool}`);
  console.log(`  FlashLoan: ${deployedAddresses.flashLoan}`);

  console.log("\n🏛️  Governance:");
  console.log(`  CredLendGovernor: ${deployedAddresses.governor}`);
  console.log(`  SafetyModule: ${deployedAddresses.safetyModule}`);

  console.log("\n🔗 Block Explorer:");
  console.log("https://creditcoin-testnet.blockscout.com\n");

  console.log("✅ Deployment addresses saved to: deployments/creditcoin-testnet.json\n");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:");
    console.error(error);
    process.exit(1);
  });
