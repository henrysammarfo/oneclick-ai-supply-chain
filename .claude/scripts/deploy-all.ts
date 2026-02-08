import hre from "hardhat";
import { ethers } from "ethers";
import fs from "fs";
import path from "path";

/**
 * Main deployment script for CredLend Protocol
 * Deploys all contracts in correct order and saves addresses
 */

interface DeployedContracts {
  testTokens: {
    tUSDC: string;
    tUSDT: string;
    tDAI: string;
    tETH: string;
    tWBTC: string;
  };
  credToken: string;
  creditScoring: string;
  uscAttestor: string;
  creditNFT: string;
  interestRateStrategy: string;
  aTokens: { [key: string]: string };
  variableDebtTokens: { [key: string]: string };
  stableDebtTokens: { [key: string]: string };
  lendingPool: string;
  flashLoan: string;
  governor: string;
  safetyModule: string;
}

async function main() {
  console.log("🚀 Starting CredLend Protocol Deployment on Creditcoin Testnet...\n");

  const [deployer] = await hre.ethers.getSigners();
  console.log("📍 Deploying from address:", deployer.address);
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("💰 Account balance:", ethers.formatEther(balance), "CTC\n");

  const deployedContracts: Partial<DeployedContracts> = {
    testTokens: {} as any,
    aTokens: {},
    variableDebtTokens: {},
    stableDebtTokens: {},
  };

  // ========================================
  // STEP 1: Deploy Test Tokens
  // ========================================
  console.log("📦 Step 1: Deploying Test Tokens...");

  const testTokenConfigs = [
    { name: "tUSDC", contractName: "TestUSDC" },
    { name: "tUSDT", contractName: "TestUSDT" },
    { name: "tDAI", contractName: "TestDAI" },
    { name: "tETH", contractName: "TestETH" },
    { name: "tWBTC", contractName: "TestWBTC" },
  ];

  for (const config of testTokenConfigs) {
    console.log(`  Deploying ${config.name}...`);
    const Token = await hre.ethers.getContractFactory(config.contractName);
    const token = await Token.deploy();
    await token.waitForDeployment();
    const address = await token.getAddress();
    deployedContracts.testTokens![config.name as keyof typeof deployedContracts.testTokens] = address;
    console.log(`  ✅ ${config.name} deployed at:`, address);
  }

  console.log("\n");

  // ========================================
  // STEP 2: Deploy CRED Governance Token
  // ========================================
  console.log("📦 Step 2: Deploying CRED Governance Token...");
  const CredToken = await hre.ethers.getContractFactory("CredToken");
  const credToken = await CredToken.deploy();
  await credToken.waitForDeployment();
  deployedContracts.credToken = await credToken.getAddress();
  console.log("  ✅ CredToken deployed at:", deployedContracts.credToken);
  console.log("\n");

  // ========================================
  // STEP 3: Deploy USC Attestor
  // ========================================
  console.log("📦 Step 3: Deploying USC Attestor...");
  const USCAttestor = await hre.ethers.getContractFactory("USCAttestor");
  const uscAttestor = await USCAttestor.deploy();
  await uscAttestor.waitForDeployment();
  deployedContracts.uscAttestor = await uscAttestor.getAddress();
  console.log("  ✅ USCAttestor deployed at:", deployedContracts.uscAttestor);
  console.log("\n");

  // ========================================
  // STEP 4: Deploy Credit Scoring
  // ========================================
  console.log("📦 Step 4: Deploying Credit Scoring...");
  const CreditScoring = await hre.ethers.getContractFactory("CreditScoring");
  const creditScoring = await CreditScoring.deploy();
  await creditScoring.waitForDeployment();
  deployedContracts.creditScoring = await creditScoring.getAddress();
  console.log("  ✅ CreditScoring deployed at:", deployedContracts.creditScoring);

  // Set USC Attestor
  console.log("  Setting USC Attestor...");
  await creditScoring.setUSCAttestor(deployedContracts.uscAttestor);
  console.log("  ✅ USC Attestor configured");
  console.log("\n");

  // ========================================
  // STEP 5: Deploy Credit NFT
  // ========================================
  console.log("📦 Step 5: Deploying Credit NFT...");
  const CreditNFT = await hre.ethers.getContractFactory("CreditNFT");
  const creditNFT = await CreditNFT.deploy();
  await creditNFT.waitForDeployment();
  deployedContracts.creditNFT = await creditNFT.getAddress();
  console.log("  ✅ CreditNFT deployed at:", deployedContracts.creditNFT);
  console.log("\n");

  // ========================================
  // STEP 6: Deploy Interest Rate Strategy
  // ========================================
  console.log("📦 Step 6: Deploying Interest Rate Strategy...");
  const InterestRateStrategy = await hre.ethers.getContractFactory("InterestRateStrategy");
  const interestRateStrategy = await InterestRateStrategy.deploy(
    deployedContracts.creditScoring
  );
  await interestRateStrategy.waitForDeployment();
  deployedContracts.interestRateStrategy = await interestRateStrategy.getAddress();
  console.log("  ✅ InterestRateStrategy deployed at:", deployedContracts.interestRateStrategy);
  console.log("\n");

  // ========================================
  // STEP 7: Deploy Token Implementations
  // ========================================
  console.log("📦 Step 7: Deploying AToken and DebtToken Implementations...");

  const assets = ["tUSDC", "tUSDT", "tDAI", "tETH", "tWBTC"];

  for (const asset of assets) {
    const underlyingAddress = deployedContracts.testTokens![asset as keyof typeof deployedContracts.testTokens];

    // Deploy AToken
    console.log(`  Deploying AToken for ${asset}...`);
    const AToken = await hre.ethers.getContractFactory("AToken");
    const aToken = await AToken.deploy(
      underlyingAddress,
      `CredLend ${asset}`,
      `a${asset}`
    );
    await aToken.waitForDeployment();
    deployedContracts.aTokens![asset] = await aToken.getAddress();
    console.log(`  ✅ a${asset} deployed at:`, deployedContracts.aTokens![asset]);

    // Deploy VariableDebtToken
    console.log(`  Deploying VariableDebtToken for ${asset}...`);
    const VariableDebtToken = await hre.ethers.getContractFactory("VariableDebtToken");
    const variableDebtToken = await VariableDebtToken.deploy(
      underlyingAddress,
      `CredLend Variable Debt ${asset}`,
      `variableDebt${asset}`
    );
    await variableDebtToken.waitForDeployment();
    deployedContracts.variableDebtTokens![asset] = await variableDebtToken.getAddress();
    console.log(`  ✅ variableDebt${asset} deployed at:`, deployedContracts.variableDebtTokens![asset]);

    // Deploy StableDebtToken
    console.log(`  Deploying StableDebtToken for ${asset}...`);
    const StableDebtToken = await hre.ethers.getContractFactory("StableDebtToken");
    const stableDebtToken = await StableDebtToken.deploy(
      underlyingAddress,
      `CredLend Stable Debt ${asset}`,
      `stableDebt${asset}`
    );
    await stableDebtToken.waitForDeployment();
    deployedContracts.stableDebtTokens![asset] = await stableDebtToken.getAddress();
    console.log(`  ✅ stableDebt${asset} deployed at:`, deployedContracts.stableDebtTokens![asset]);
    console.log("");
  }

  // ========================================
  // STEP 8: Deploy Lending Pool
  // ========================================
  console.log("📦 Step 8: Deploying Lending Pool...");
  const LendingPool = await hre.ethers.getContractFactory("LendingPool");
  const lendingPool = await LendingPool.deploy(
    deployedContracts.creditScoring,
    deployedContracts.credToken
  );
  await lendingPool.waitForDeployment();
  deployedContracts.lendingPool = await lendingPool.getAddress();
  console.log("  ✅ LendingPool deployed at:", deployedContracts.lendingPool);
  console.log("\n");

  // ========================================
  // STEP 9: Deploy Flash Loan
  // ========================================
  console.log("📦 Step 9: Deploying Flash Loan...");
  const FlashLoan = await hre.ethers.getContractFactory("FlashLoan");
  const flashLoan = await FlashLoan.deploy(deployedContracts.creditScoring);
  await flashLoan.waitForDeployment();
  deployedContracts.flashLoan = await flashLoan.getAddress();
  console.log("  ✅ FlashLoan deployed at:", deployedContracts.flashLoan);
  console.log("\n");

  // ========================================
  // STEP 10: Deploy Governance
  // ========================================
  console.log("📦 Step 10: Deploying Governance...");
  const CredLendGovernor = await hre.ethers.getContractFactory("CredLendGovernor");
  const governor = await CredLendGovernor.deploy(deployedContracts.credToken);
  await governor.waitForDeployment();
  deployedContracts.governor = await governor.getAddress();
  console.log("  ✅ CredLendGovernor deployed at:", deployedContracts.governor);
  console.log("\n");

  // ========================================
  // STEP 11: Deploy Safety Module
  // ========================================
  console.log("📦 Step 11: Deploying Safety Module...");
  const SafetyModule = await hre.ethers.getContractFactory("SafetyModule");
  const safetyModule = await SafetyModule.deploy(deployedContracts.credToken);
  await safetyModule.waitForDeployment();
  deployedContracts.safetyModule = await safetyModule.getAddress();
  console.log("  ✅ SafetyModule deployed at:", deployedContracts.safetyModule);
  console.log("\n");

  // ========================================
  // STEP 12: Configure Roles and Permissions
  // ========================================
  console.log("📦 Step 12: Configuring Roles and Permissions...");

  // Grant roles to LendingPool
  console.log("  Granting MINTER_ROLE to LendingPool on CredToken...");
  const MINTER_ROLE = hre.ethers.keccak256(hre.ethers.toUtf8Bytes("MINTER_ROLE"));
  await credToken.grantRole(MINTER_ROLE, deployedContracts.lendingPool);

  console.log("  Granting REWARDS_ROLE to LendingPool on CredToken...");
  const REWARDS_ROLE = hre.ethers.keccak256(hre.ethers.toUtf8Bytes("REWARDS_ROLE"));
  await credToken.grantRole(REWARDS_ROLE, deployedContracts.lendingPool);

  console.log("  Granting SCORER_ROLE to LendingPool on CreditScoring...");
  const SCORER_ROLE = hre.ethers.keccak256(hre.ethers.toUtf8Bytes("SCORER_ROLE"));
  await creditScoring.grantRole(SCORER_ROLE, deployedContracts.lendingPool);

  console.log("  Granting MINTER_ROLE to CreditScoring on CreditNFT...");
  await creditNFT.grantRole(MINTER_ROLE, deployedContracts.creditScoring);

  console.log("  Granting UPDATER_ROLE to CreditScoring on CreditNFT...");
  const UPDATER_ROLE = hre.ethers.keccak256(hre.ethers.toUtf8Bytes("UPDATER_ROLE"));
  await creditNFT.grantRole(UPDATER_ROLE, deployedContracts.creditScoring);

  console.log("  ✅ All roles configured");
  console.log("\n");

  // ========================================
  // STEP 13: Initialize Reserves in Lending Pool
  // ========================================
  console.log("📦 Step 13: Initializing Reserves in Lending Pool...");

  for (const asset of assets) {
    console.log(`  Initializing reserve for ${asset}...`);
    const underlyingAddress = deployedContracts.testTokens![asset as keyof typeof deployedContracts.testTokens];

    await lendingPool.initReserve(
      underlyingAddress,
      deployedContracts.aTokens![asset],
      deployedContracts.stableDebtTokens![asset],
      deployedContracts.variableDebtTokens![asset],
      deployedContracts.interestRateStrategy
    );

    console.log(`  ✅ ${asset} reserve initialized`);
  }

  console.log("\n");

  // ========================================
  // Save Deployment Addresses
  // ========================================
  console.log("📝 Saving deployment addresses...");

  const deploymentData = {
    network: "creditcoin_testnet",
    chainId: 102031,
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
    contracts: deployedContracts,
  };

  const deploymentsDir = path.join(__dirname, "..", "deployments");
  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir, { recursive: true });
  }

  const filePath = path.join(deploymentsDir, "creditcoin-testnet.json");
  fs.writeFileSync(filePath, JSON.stringify(deploymentData, null, 2));

  console.log("✅ Deployment addresses saved to:", filePath);
  console.log("\n");

  // ========================================
  // Deployment Summary
  // ========================================
  console.log("🎉 ========================");
  console.log("🎉 DEPLOYMENT COMPLETE!");
  console.log("🎉 ========================\n");

  console.log("📋 Contract Addresses:");
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log("\n🪙 Test Tokens:");
  for (const [name, address] of Object.entries(deployedContracts.testTokens!)) {
    console.log(`  ${name}: ${address}`);
  }

  console.log("\n🏛️ Core Contracts:");
  console.log(`  CredToken: ${deployedContracts.credToken}`);
  console.log(`  CreditScoring: ${deployedContracts.creditScoring}`);
  console.log(`  USCAttestor: ${deployedContracts.uscAttestor}`);
  console.log(`  CreditNFT: ${deployedContracts.creditNFT}`);
  console.log(`  InterestRateStrategy: ${deployedContracts.interestRateStrategy}`);
  console.log(`  LendingPool: ${deployedContracts.lendingPool}`);
  console.log(`  FlashLoan: ${deployedContracts.flashLoan}`);

  console.log("\n🏛️ Governance:");
  console.log(`  CredLendGovernor: ${deployedContracts.governor}`);
  console.log(`  SafetyModule: ${deployedContracts.safetyModule}`);

  console.log("\n");
  console.log("🔗 Block Explorer:");
  console.log("https://creditcoin-testnet.blockscout.com");
  console.log("\n");

  console.log("✅ Next Steps:");
  console.log("1. Verify contracts on Blockscout");
  console.log("2. Test faucet functions for all test tokens");
  console.log("3. Test lending and borrowing flows");
  console.log("4. Test credit scoring updates");
  console.log("5. Test cross-chain USC verification");
  console.log("\n");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:");
    console.error(error);
    process.exit(1);
  });
