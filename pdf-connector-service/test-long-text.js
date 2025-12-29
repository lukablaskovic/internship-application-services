import axios from "axios";

/**
 * Test script for PDF generation with long text
 * Tests the PDF generator with various text lengths to ensure no horizontal overflow
 */

const SERVICE_URL = "http://localhost:8084";

// Test data with very long task description (over 200 characters)
const testData = {
  student_ime: "Marko",
  student_prezime: "Horvat",
  student_email: "mhorvat@student.unipu.hr",
  student_broj_mobitela: "+385912345678",
  student_OIB: "12345678901",
  Poslodavac: "Tech Company d.o.o.",
  mentor_ime: "Ana",
  mentor_prezime: "Kovačić",
  pocetak_prakse: "01.02.2024",
  kraj_prakse: "30.04.2024",
  dogovoreni_broj_sati: "160",
  detaljan_opis_zadatka:
    "Student će raditi na razvoju web aplikacije koristeći raditi na razvoju web aplikacije koristeći moderneraditi na razvoju web aplikacije koristeći moderneraditi na razvoju web aplikacije koristeći moderneraditi na razvoju web aplikacije koristeći moderneraditi na razvoju web aplikacije koristeći moderne moderne JavaScript frameworke i biblioteke. Zadatak uključuje dizajniranje i implementaciju korisničkog sučelja, integraciju s REST API-jem, upravljanje stanjem aplikacije, optimizaciju performansi, testiranje komponenata, te suradnju s backend timom na implementaciji novih funkcionalnosti. Također će biti uključen u code review proces i prisustvovati dnevnim stand-up sastancima tima. Student će koristiti Git za verzioniranje koda i raditi u Agile okruženju s dvotjednim sprintovima. Očekuje se da će steći praktično iskustvo u profesionalnom razvoju softvera i naučiti dobre razvojne prakse koje se koriste u industriji. Na kraju prakse, student bi trebao biti sposoban samostalno razvijati komponente i rješavati zadatke srednjeg nivoa kompleksnosti.",
};

// Test data with extremely long task description (over 500 characters)
const testDataExtraLong = {
  student_ime: "Petra",
  student_prezime: "Marić",
  student_email: "pmaric@student.unipu.hr",
  student_broj_mobitela: "+385923456789",
  student_OIB: "98765432109",
  Poslodavac: "Innovation Solutions d.o.o.",
  mentor_ime: "Ivan",
  mentor_prezime: "Babić",
  pocetak_prakse: "15.03.2024",
  kraj_prakse: "15.06.2024",
  dogovoreni_broj_sati: "240",
  detaljan_opis_zadatka:
    "Student će biti uključen u kompleksan projekt razvoja enterprise aplikacije koja uključuje mikroservisnu arhitekturu, distribuirane sustave, i napredne sigurnosne mehanizme. Zadatak obuhvaća dizajn i implementaciju RESTful i GraphQL API-ja, rad s bazama podataka (PostgreSQL, MongoDB, Redis), implementaciju autentifikacije i autorizacije koristeći JWT tokene i OAuth2 protokol, pisanje unit i integration testova koristeći Jest i Supertest, containerizaciju aplikacija pomoću Dockera, postavljanje CI/CD pipeline-ova, monitoring i logging korištenjem ELK stack-a, te optimizaciju performansi i skalabilnosti sustava. Student će također raditi na implementaciji real-time funkcionalnosti koristeći WebSocket protokol, integraciji s vanjskim API-jima, i razvoju administratorskog panela. Kroz praksu će biti izložen agile metodologiji, Scrum ceremonijama, pair programming sesijama, i code review procesima. Očekuje se da će student razviti dublje razumijevanje best practices u profesionalnom razvoju softvera, naučiti raditi u timu, koristiti moderne razvojne alate i tehnologije, te steći iskustvo koje će ga pripremiti za karijeru u softverskom inženjerstvu. Mentor će pružati kontinuiranu podršku i feedback kroz cijeli period prakse.",
};

// Test data with very long words/URLs that shouldn't break layout
const testDataLongWords = {
  student_ime: "Luka",
  student_prezime: "Novak",
  student_email: "lnovak@student.unipu.hr",
  student_broj_mobitela: "+385934567890",
  student_OIB: "11122233344",
  Poslodavac: "Digital Agency d.o.o.",
  mentor_ime: "Marija",
  mentor_prezime: "Jurić",
  pocetak_prakse: "01.04.2024",
  kraj_prakse: "30.06.2024",
  dogovoreni_broj_sati: "200",
  detaljan_opis_zadatka:
    "Student će raditi na projektu koji koristi tehnologije poput React.js, Node.js, Express.js, MongoDB, Docker, Kubernetes, GitHub, GitLab, CircleCI, Jest, Enzyme, Webpack, Babel, ESLint, Prettier, TypeScript. Zadatak uključuje rad s URL-ovima kao što su https://api.example.com/v1/users/12345/profile/detailed-information/personal-data/contact-details i dugim nazivima package-a poput @organization-name/very-long-package-name-with-multiple-parts-and-descriptive-naming-convention-following-semantic-versioning-v2-0-0-beta-release-candidate-1. VeryLongClassNameThatDoesntHaveSpacesAndCouldPotentiallyCauseOverflowIssuesIfNotHandledProperlyInTheLayoutSystemWithWordWrappingEnabled.",
};

async function testPDFGeneration(testName, data) {
  try {
    console.log(`\n🧪 Running test: ${testName}`);
    console.log(
      `📝 Task description length: ${data.detaljan_opis_zadatka.length} characters`
    );

    const response = await axios.post(`${SERVICE_URL}/api/potvrda`, data, {
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (response.status === 200 && response.data.pdf_attachment_url) {
      console.log(`✅ SUCCESS: PDF generated successfully`);
      console.log(`📄 PDF URL: ${response.data.pdf_attachment_url}`);
      return true;
    } else {
      console.log(`❌ FAILED: Unexpected response`);
      console.log(response.data);
      return false;
    }
  } catch (error) {
    console.log(`❌ ERROR: ${error.message}`);
    if (error.response) {
      console.log(`Status: ${error.response.status}`);
      console.log(`Data:`, error.response.data);
    }
    return false;
  }
}

async function runAllTests() {
  console.log("🚀 Starting PDF generation tests with long text...");
  console.log(`📍 Service URL: ${SERVICE_URL}`);

  // Check if service is running
  try {
    await axios.get(`${SERVICE_URL}/status`);
    console.log("✅ Service is running\n");
  } catch (error) {
    console.log("❌ Service is not running. Please start the service first.");
    console.log("   Run: npm start or node server.js");
    process.exit(1);
  }

  const results = [];

  // Run tests
  results.push(
    await testPDFGeneration("Test 1: Standard long text (>200 chars)", testData)
  );
  results.push(
    await testPDFGeneration(
      "Test 2: Extra long text (>500 chars)",
      testDataExtraLong
    )
  );
  results.push(
    await testPDFGeneration("Test 3: Long words and URLs", testDataLongWords)
  );

  // Summary
  console.log("\n" + "=".repeat(60));
  console.log("📊 TEST SUMMARY");
  console.log("=".repeat(60));
  const passed = results.filter((r) => r).length;
  const failed = results.filter((r) => !r).length;
  console.log(`Total tests: ${results.length}`);
  console.log(`✅ Passed: ${passed}`);
  console.log(`❌ Failed: ${failed}`);
  console.log("=".repeat(60));

  if (failed === 0) {
    console.log(
      "\n🎉 All tests passed! Check the generated PDFs to verify text wrapping."
    );
  } else {
    console.log("\n⚠️  Some tests failed. Please check the errors above.");
  }
}

// Run tests
runAllTests().catch(console.error);
